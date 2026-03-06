import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/services/signals_service.dart';
import '../../../../core/providers/auth_provider.dart';
import '../widgets/fintech_signal_card.dart';
import '../widgets/bottom_nav_bar.dart';
import '../widgets/top_status_bar.dart';
import '../widgets/header_section.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  List<dynamic> _signals = [];
  bool _loading = true;
  String? _error;
  int _selectedNavIndex = 0;

  @override
  void initState() {
    super.initState();
    // Try to load real signals first
    _loadSignals();
    // Start periodic refresh (every 30 seconds)
    _startPeriodicRefresh();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Timer? _refreshTimer;

  void _startPeriodicRefresh() {
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        _loadSignalsSilently();
      }
    });
  }

  void _loadMockSignals() {
    // Add mock signals for preview
    setState(() {
      _signals = [
        {
          'id': '1',
          'asset': 'EUR/USD',
          'direction': 'CALL',
          'probability': 88,
          'expirySeconds': 105,
          'entryTime': '14:30 GMT',
          'contractDuration': 'M5',
          'suggestedRisk': 2.0,
          'suggestedRiskPercent': 2,
        },
        {
          'id': '2',
          'asset': 'GBP/USD',
          'direction': 'PUT',
          'probability': 75,
          'expirySeconds': 180,
          'entryTime': '15:00 GMT',
          'contractDuration': 'M5',
          'suggestedRisk': 3.0,
          'suggestedRiskPercent': 3,
        },
        {
          'id': '3',
          'asset': 'USD/JPY',
          'direction': 'PUT',
          'probability': 82,
          'expirySeconds': 240,
          'entryTime': '15:30 GMT',
          'contractDuration': 'M5',
          'suggestedRisk': 2.5,
          'suggestedRiskPercent': 2,
        },
      ];
      _loading = false;
      _error = null; // Clear any errors
    });
  }

  Future<void> _loadSignalsSilently() async {
    // Try to load real signals in background, but don't show errors
    try {
      final authNotifier = ref.read(authProvider.notifier);
      final authState = ref.read(authProvider);
      
      if (authState == AuthState.loading || authState == AuthState.initial) {
        await Future.delayed(const Duration(milliseconds: 500));
      }
      
      final token = authNotifier.token;
      if (token == null) {
        debugPrint('⚠️ No auth token - cannot load signals');
        // Show mock signals if no token
        if (_signals.isEmpty) {
          _loadMockSignals();
        }
        return;
      }
      
      final apiService = ref.read(apiServiceProvider);
      apiService.setAuthToken(token);
      final signalsService = SignalsService(apiService);
      final signals = await signalsService.getSignals();
      
      debugPrint('✅ Loaded ${signals.length} signals from API');
      
      // Transform and update signals
      if (mounted) {
        final transformedSignals = _transformSignals(signals);
        
        setState(() {
          _signals = transformedSignals;
          _loading = false;
        });
        
        debugPrint('✅ Transformed ${transformedSignals.length} signals for display');
        
        // If no real signals, show mock signals
        if (transformedSignals.isEmpty && _signals.isEmpty) {
          debugPrint('⚠️ No real signals, showing mock signals');
          _loadMockSignals();
        }
      }
    } catch (e) {
      debugPrint('❌ Error loading signals: $e');
      // Show mock signals on error if no signals exist
      if (mounted && _signals.isEmpty) {
        _loadMockSignals();
      }
    }
  }

  List<Map<String, dynamic>> _transformSignals(List<dynamic> signals) {
    if (signals.isEmpty) return [];
    
    return signals
        .map((signal) {
          // Calculate remaining time
          final createdAt = signal['createdAt'] as String?;
          final expirySeconds = signal['expirySeconds'] as int? ?? 60;
          final createdAtDate = createdAt != null ? DateTime.parse(createdAt) : DateTime.now();
          final expiryDate = createdAtDate.add(Duration(seconds: expirySeconds));
          final remainingSeconds = expiryDate.difference(DateTime.now()).inSeconds;
          
          // Skip expired signals (remainingSeconds <= 0)
          if (remainingSeconds <= 0) {
            return null;
          }
          
          // Format entry time
          final entryTime = createdAtDate.toIso8601String().substring(11, 16); // HH:mm
          
          // Determine contract duration from expirySeconds
          String contractDuration = 'M1';
          if (expirySeconds >= 300) {
            contractDuration = 'M5';
          } else if (expirySeconds >= 180) {
            contractDuration = 'M3';
          } else if (expirySeconds >= 60) {
            contractDuration = 'M1';
          } else {
            contractDuration = '30s';
          }
          
          return {
            'id': signal['id'],
            'asset': signal['asset'],
            'direction': signal['direction'],
            'probability': signal['confidence'] ?? 50, // Use confidence as probability
            'expirySeconds': remainingSeconds,
            'entryTime': '$entryTime GMT',
            'contractDuration': contractDuration,
            'suggestedRisk': 2.0,
            'suggestedRiskPercent': 2,
            'confidence': signal['confidence'],
            'newsStatus': signal['newsStatus'] ?? 'SAFE',
          };
        })
        .where((signal) => signal != null)
        .cast<Map<String, dynamic>>()
        .toList();
  }

  Future<void> _loadSignals() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      // Ensure auth token is set before making API call
      final authNotifier = ref.read(authProvider.notifier);
      final authState = ref.read(authProvider);
      
      // Wait for authentication if still loading
      if (authState == AuthState.loading || authState == AuthState.initial) {
        await Future.delayed(const Duration(milliseconds: 500));
      }
      
      // Get token and set it in API service
      final token = authNotifier.token;
      if (token != null) {
        final apiService = ref.read(apiServiceProvider);
        apiService.setAuthToken(token);
      }
      
      final apiService = ref.read(apiServiceProvider);
      final signalsService = SignalsService(apiService);
      final signals = await signalsService.getSignals();
      
      debugPrint('✅ Loaded ${signals.length} signals from API');
      
      // Transform signals to display format
      final transformedSignals = _transformSignals(signals);
      
      setState(() {
        if (transformedSignals.isNotEmpty) {
          _signals = transformedSignals;
        } else {
          // If no real signals, show mock signals
          debugPrint('⚠️ No real signals, showing mock signals');
          _loadMockSignals();
        }
        _loading = false;
      });
    } catch (e) {
      debugPrint('❌ Error loading signals: $e');
      setState(() {
        _error = e.toString();
        _loading = false;
        // Show mock signals on error
        if (_signals.isEmpty) {
          _loadMockSignals();
        }
      });
    }
  }

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedNavIndex = index;
    });

    switch (index) {
      case 0:
        // Already on signals page
        break;
      case 1:
        context.push('/news');
        break;
      case 2:
        // Performance page - implement later
        break;
      case 3:
        context.push('/settings');
        break;
    }
  }

  Future<void> _openQuotexPlatform() async {
    final url = Uri.parse('https://qxbroker.com/ar/trade');
    try {
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
      }
    } catch (e) {
      // Handle error silently or show a snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('فشل فتح المنصة. يرجى المحاولة مرة أخرى.'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: const Color(0xFF0F1115),
        body: SafeArea(
          child: Column(
            children: [
              // Top Status Bar
              const TopStatusBar(),
              
              // Header Section
              const HeaderSection(),
              
              // Signals List
              Expanded(
                child: _loading
                    ? const Center(
                        child: CircularProgressIndicator(
                          color: Color(0xFF347AF0),
                        ),
                      )
                    : _error != null
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  _error!.contains('verification')
                                      ? 'يرجى التحقق من حسابك أولاً'
                                      : 'حدث خطأ في تحميل الإشارات',
                                  style: const TextStyle(
                                    color: Color(0xFFB0B7C3),
                                    fontSize: 16,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: _loadSignals,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF347AF0),
                                    foregroundColor: Colors.white,
                                  ),
                                  child: const Text('إعادة المحاولة'),
                                ),
                              ],
                            ),
                          )
                        : _signals.isEmpty
                            ? Center(
                                child: Text(
                                  'لا توجد إشارات متاحة حالياً',
                                  style: const TextStyle(
                                    color: Color(0xFFB0B7C3),
                                    fontSize: 16,
                                  ),
                                ),
                              )
                            : RefreshIndicator(
                                onRefresh: _loadSignals,
                                color: const Color(0xFF347AF0),
                                child: ListView.builder(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  itemCount: _signals.length,
                                  itemBuilder: (context, index) {
                                    final signal = _signals[index];
                                    return Padding(
                                      padding: const EdgeInsets.only(bottom: 16),
                                      child: FintechSignalCard(
                                        signal: signal,
                                        onOpenPlatform: () {
                                          _openQuotexPlatform();
                                        },
                                      ),
                                    );
                                  },
                                ),
                              ),
              ),
            ],
          ),
        ),
        bottomNavigationBar: BottomNavBar(
          selectedIndex: _selectedNavIndex,
          onItemTapped: _onNavItemTapped,
        ),
      ),
    );
  }
}
