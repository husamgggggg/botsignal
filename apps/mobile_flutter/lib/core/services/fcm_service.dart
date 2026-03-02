// import 'package:firebase_messaging/firebase_messaging.dart'; // Disabled for web compatibility
import 'package:flutter/foundation.dart';

class FcmService {
  // Firebase Messaging disabled for web compatibility
  // final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  String? _fcmToken;

  Future<String?> getToken() async {
    // FCM disabled for now - enable when needed for mobile
    debugPrint('FCM disabled - not configured');
    return null;
    // try {
    //   if (kIsWeb) {
    //     debugPrint('FCM not supported on web');
    //     return null;
    //   }
    //   _fcmToken = await _messaging.getToken();
    //   return _fcmToken;
    // } catch (e) {
    //   debugPrint('Error getting FCM token: $e');
    //   return null;
    // }
  }

  Future<void> requestPermission() async {
    // FCM disabled for now
    debugPrint('FCM disabled - skipping permission request');
    // try {
    //   if (kIsWeb) {
    //     return;
    //   }
    //   final settings = await _messaging.requestPermission(
    //     alert: true,
    //     badge: true,
    //     sound: true,
    //   );
    //   debugPrint('FCM Permission status: ${settings.authorizationStatus}');
    // } catch (e) {
    //   debugPrint('Error requesting FCM permission: $e');
    // }
  }

  void configureForegroundHandler() {
    // FCM disabled
    // FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    //   debugPrint('Got a message whilst in the foreground!');
    //   debugPrint('Message data: ${message.data}');
    //   if (message.notification != null) {
    //     debugPrint('Message notification: ${message.notification?.title}');
    //   }
    // });
  }

  void configureBackgroundHandler() {
    // FCM disabled
    // FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  }
}

// @pragma('vm:entry-point')
// Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
//   debugPrint('Handling a background message: ${message.messageId}');
// }

