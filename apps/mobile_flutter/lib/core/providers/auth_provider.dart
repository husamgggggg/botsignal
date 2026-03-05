import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/fcm_service.dart';

final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

final sharedPreferencesProvider = FutureProvider<SharedPreferences>((ref) async {
  return await SharedPreferences.getInstance();
});

final authServiceProvider = FutureProvider<AuthService>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final prefs = await ref.watch(sharedPreferencesProvider.future);
  return AuthService(apiService, prefs);
});

final fcmServiceProvider = Provider<FcmService>((ref) => FcmService());

enum AuthState {
  initial,
  loading,
  authenticated,
  unauthenticated,
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthService? _authService;
  final FcmService _fcmService;
  final Ref _ref;
  String? _token;
  String? _deviceId;
  bool _disposed = false;

  AuthNotifier(this._authService, this._fcmService, this._ref) : super(AuthState.initial);
  
  void setAuthService(AuthService authService) {
    if (_disposed) return;
    _authService = authService;
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }

  Future<void> initialize(String deviceId) async {
    if (_disposed) return;
    _deviceId = deviceId;
    state = AuthState.loading;

    // Wait for authService to be ready if not already available
    if (_authService == null) {
      // Wait for the authService provider to be ready
      // Use a polling approach that doesn't use ref.read during rebuild
      AuthService? service;
      int attempts = 0;
      while (service == null && attempts < 30) {
        // Wait a bit before checking
        await Future.delayed(const Duration(milliseconds: 50));
        
        // Try to get service from the provider state
        // We can't use _ref.read here, so we'll wait for it to be set via listener
        // or check if it's available through the provider's current state
        if (_authService != null) {
          service = _authService;
          break;
        }
        
        attempts++;
      }
      
      if (service == null && _authService == null) {
        // If still null, throw error
        throw StateError('Failed to initialize AuthService: service not available');
      }
    }

    // Check for existing token
    if (_disposed) return;
    final token = _authService!.getToken();
    if (token != null) {
      _token = token;
      final apiService = _ref.read(apiServiceProvider);
      apiService.setAuthToken(token);
      if (!_disposed) {
        state = AuthState.authenticated;
      }
    } else {
      // Register device
      try {
        await _fcmService.requestPermission();
        if (_disposed) return;
        final fcmToken = await _fcmService.getToken();
        final response = await _authService!.registerDevice(deviceId, fcmToken: fcmToken);
        _token = response['token'];
        await _authService!.saveToken(_token!);
        final apiService = _ref.read(apiServiceProvider);
        apiService.setAuthToken(_token!);
        if (!_disposed) {
          state = AuthState.authenticated;
        }
      } catch (e) {
        if (!_disposed) {
          state = AuthState.unauthenticated;
        }
      }
    }
  }

  Future<void> logout() async {
    if (_disposed) return;
    if (_authService != null) {
      await _authService!.clearToken();
    }
    _token = null;
    if (!_disposed) {
      state = AuthState.unauthenticated;
    }
  }

  String? get token => _token;
  String? get deviceId => _deviceId;
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authServiceAsync = ref.watch(authServiceProvider);
  final fcmService = ref.watch(fcmServiceProvider);
  
  // Get authService synchronously if available, otherwise create notifier that will wait
  final authService = authServiceAsync.maybeWhen(
    data: (service) => service,
    orElse: () => null,
  );
  
  final notifier = AuthNotifier(authService, fcmService, ref);
  
  // Listen to authServiceProvider changes and update notifier when ready
  ref.listen<AsyncValue<AuthService>>(authServiceProvider, (previous, next) {
    next.whenData((service) {
      if (notifier._authService == null) {
        notifier.setAuthService(service);
      }
    });
  });
  
  return notifier;
});

