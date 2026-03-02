import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/services/platforms_service.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/services/verify_service.dart';

class PlatformSelectScreen extends ConsumerStatefulWidget {
  const PlatformSelectScreen({super.key});

  @override
  ConsumerState<PlatformSelectScreen> createState() => _PlatformSelectScreenState();
}

class _PlatformSelectScreenState extends ConsumerState<PlatformSelectScreen> {
  String? _selectedPlatform;
  final _accountIdController = TextEditingController();
  
  // Initialize with default platforms so buttons appear immediately
  Map<String, dynamic> _platforms = {
    'platforms': [
      {
        'id': 'QUOTEX',
        'name': 'Quotex',
        'nameAr': 'كووتكس',
        'descriptionAr': 'منصة متخصصة في تداول الخيارات الثنائية والرقمية.',
        'descriptionEn': 'A specialized platform for binary and digital options trading.',
      },
      {
        'id': 'POCKET_OPTION',
        'name': 'Pocket Option',
        'nameAr': 'بوكيت أوبشن',
        'descriptionAr': 'منصة للوصول إلى أدوات تداول الخيارات الرقمية.',
        'descriptionEn': 'A platform for accessing digital options trading tools.',
      },
    ]
  };

  @override
  void initState() {
    super.initState();
    _loadPlatforms();
  }

  @override
  void dispose() {
    _accountIdController.dispose();
    super.dispose();
  }

  Future<void> _loadPlatforms() async {
    if (!mounted) return;
    
    try {
      // Ensure we have a valid ref context
      final apiService = ref.read(apiServiceProvider);
      final service = PlatformsService(apiService);
      final platforms = await service.getPlatforms()
          .timeout(
            const Duration(seconds: 5),
            onTimeout: () {
              throw TimeoutException('Connection timeout');
            },
          );
      if (mounted && platforms['platforms'] != null) {
        // Ensure all platforms have required fields
        final platformsList = (platforms['platforms'] as List).map((p) {
          final platform = Map<String, dynamic>.from(p);
          // Add default descriptions if missing
          if (!platform.containsKey('descriptionAr')) {
            platform['descriptionAr'] = platform['nameAr'] == 'كووتكس'
                ? 'منصة متخصصة في تداول الخيارات الثنائية والرقمية.'
                : 'منصة للوصول إلى أدوات تداول الخيارات الرقمية.';
          }
          if (!platform.containsKey('descriptionEn')) {
            platform['descriptionEn'] = platform['name'] == 'Quotex'
                ? 'A specialized platform for binary and digital options trading.'
                : 'A platform for accessing digital options trading tools.';
          }
          return platform;
        }).toList();
        
        setState(() {
          _platforms = {'platforms': platformsList};
        });
      }
    } catch (e) {
      debugPrint('Failed to load platforms from API: $e');
      // Keep default platforms on error
    }
  }

  Future<void> _continue() async {
    if (_selectedPlatform == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('الرجاء اختيار منصة')),
        );
      }
      return;
    }

    if (_accountIdController.text.trim().isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('الرجاء إدخال رقم الحساب')),
        );
      }
      return;
    }

    if (!mounted) return;

    try {
      // Use ref.read in a safe way
      final apiService = ref.read(apiServiceProvider);
      final verifyService = VerifyService(apiService);
      final platformsService = PlatformsService(apiService);
      final authNotifier = ref.read(authProvider.notifier);
      final deviceId = authNotifier.deviceId ?? '';

      // Get postback configuration for the selected platform
      String? postbackUrl;
      String? lid;
      String? clickId;
      String? siteId;

      try {
        final postbackConfig = await platformsService.getPostbackConfig(_selectedPlatform!);
        if (postbackConfig != null) {
          postbackUrl = postbackConfig['postbackUrl'] as String?;
          lid = postbackConfig['lid'] as String?;
          clickId = postbackConfig['clickId'] as String?;
          siteId = postbackConfig['siteId'] as String?;
        }
      } catch (e) {
        debugPrint('Failed to get postback config: $e');
      }

      // If postback URL or LID not found, use defaults from affiliate link
      if (postbackUrl == null || postbackUrl.isEmpty) {
        postbackUrl = platformsService.getDefaultPostbackUrl(_selectedPlatform!);
      }
      
      // Get LID from affiliate link (same LID used in affiliate URL)
      if (lid == null || lid.isEmpty) {
        lid = platformsService.getLidFromAffiliateUrl(_selectedPlatform!);
      }

      final result = await verifyService.verifyAccount(
        platform: _selectedPlatform!,
        accountId: _accountIdController.text.trim(),
        deviceId: deviceId,
        postbackUrl: postbackUrl,
        lid: lid,
        clickId: clickId,
        siteId: siteId,
      );

      if (mounted) {
        final messageAr = result['message_ar'] as String? ?? '';
        final messageEn = result['message_en'] as String? ?? '';
        context.push(
          '/verify-result?status=${result['status']}&messageAr=${Uri.encodeComponent(messageAr)}&messageEn=${Uri.encodeComponent(messageEn)}&platform=${_selectedPlatform!}',
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطأ: $e')),
        );
      }
    }
  }

  Widget _buildPlatformLogo(String platformId) {
    // Map platform IDs to logo image paths
    final logoPaths = {
      'QUOTEX': 'assets/images/quotex_logo.png',
      'POCKET_OPTION': 'assets/images/pocket_option_logo.png',
    };
    
    final logoPath = logoPaths[platformId] ?? '';
    
    if (logoPath.isNotEmpty) {
      return Image.asset(
        logoPath,
        width: 80,
        height: 80,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) {
          // Fallback to icon if image not found
          return Icon(
            platformId == 'QUOTEX' ? Icons.hexagon : Icons.circle,
            color: AppTheme.neonBlue,
            size: 50,
          );
        },
      );
    }
    
    // Default icon if no logo path
    return Icon(
      platformId == 'QUOTEX' ? Icons.hexagon : Icons.circle,
      color: AppTheme.neonBlue,
      size: 50,
    );
  }

  Widget _buildLogo() {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: AppTheme.primaryBlack,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Image.asset(
          'assets/images/nexora_logo.png',
          width: 60,
          height: 60,
          fit: BoxFit.contain,
          errorBuilder: (context, error, stackTrace) {
            // Fallback if image not found
            return Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppTheme.neonBlue, AppTheme.neonGreen],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.analytics,
                color: AppTheme.primaryBlack,
                size: 32,
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildPlatformCard(Map<String, dynamic> platform, bool isSelected) {
    try {
      final isArabic = Localizations.localeOf(context).languageCode == 'ar';
      
      // Safe extraction with null checks - ensure all values are strings
      String nameAr = '';
      String nameEn = '';
      String descAr = '';
      String descEn = '';
      String platformId = '';
      
      try {
        final nameArValue = platform['nameAr'];
        nameAr = nameArValue?.toString() ?? '';
      } catch (e) {
        nameAr = '';
      }
      
      try {
        final nameEnValue = platform['name'];
        nameEn = nameEnValue?.toString() ?? '';
      } catch (e) {
        nameEn = '';
      }
      
      try {
        final descArValue = platform['descriptionAr'];
        descAr = descArValue?.toString() ?? '';
      } catch (e) {
        descAr = '';
      }
      
      try {
        final descEnValue = platform['descriptionEn'];
        descEn = descEnValue?.toString() ?? '';
      } catch (e) {
        descEn = '';
      }
      
      try {
        final idValue = platform['id'];
        platformId = idValue?.toString() ?? '';
      } catch (e) {
        platformId = '';
      }
      
      // Trim all values
      nameAr = nameAr.trim();
      nameEn = nameEn.trim();
      descAr = descAr.trim();
      descEn = descEn.trim();
      platformId = platformId.trim();
      
      final platformName = isArabic 
          ? (nameAr.isNotEmpty ? nameAr : (nameEn.isNotEmpty ? nameEn : 'Unknown'))
          : (nameEn.isNotEmpty ? nameEn : (nameAr.isNotEmpty ? nameAr : 'Unknown'));
      final description = isArabic 
          ? (descAr.isNotEmpty ? descAr : (descEn.isNotEmpty ? descEn : ''))
          : (descEn.isNotEmpty ? descEn : (descAr.isNotEmpty ? descAr : ''));

      return GestureDetector(
      onTap: () {
        final id = (platform['id'] as String? ?? platform['id']?.toString() ?? '').trim();
        if (id.isNotEmpty) {
          setState(() {
            _selectedPlatform = id;
          });
        }
      },
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.darkGray,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? AppTheme.neonBlue : AppTheme.lightGray,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppTheme.neonBlue.withValues(alpha: 0.3),
                    blurRadius: 8,
                    spreadRadius: 2,
                  ),
                ]
              : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              mainAxisSize: MainAxisSize.max,
              children: [
                // Platform Logo
                Flexible(
                  child: Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: AppTheme.lightGray,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: _buildPlatformLogo(platformId),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                // Radio button
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: isSelected ? AppTheme.neonBlue : AppTheme.textGray,
                      width: 2,
                    ),
                    color: isSelected ? AppTheme.neonBlue : Colors.transparent,
                  ),
                  child: isSelected
                      ? const Icon(
                          Icons.check,
                          size: 16,
                          color: AppTheme.primaryBlack,
                        )
                      : null,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              platformName.isNotEmpty ? platformName : 'Unknown',
              style: const TextStyle(
                color: AppTheme.textWhite,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              description.isNotEmpty ? description : '',
              style: const TextStyle(
                color: AppTheme.textGray,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
    } catch (e) {
      // Fallback UI if there's any error
      return Container(
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.darkGray,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.lightGray),
        ),
        child: const Text(
          'Error loading platform',
          style: TextStyle(color: AppTheme.textWhite),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final platformsList = (_platforms['platforms'] as List);

    return Scaffold(
      backgroundColor: AppTheme.primaryBlack,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header with Logo
              Row(
                children: [
                  _buildLogo(),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'NEXORA',
                          style: TextStyle(
                            color: AppTheme.textWhite,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'إشارات تداول مجانية',
                          style: TextStyle(
                            color: AppTheme.textGray,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 40),
              
              // Title
              const Text(
                'اختر منصة التداول',
                style: TextStyle(
                  color: AppTheme.textWhite,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'يتم تخصيص نماذج التحليل بناءً على منصة التنفيذ.',
                style: TextStyle(
                  color: AppTheme.textGray,
                  fontSize: 14,
                ),
              ),
              const SizedBox(height: 24),
              
              // Platform Cards
              Row(
                children: platformsList.map<Widget>((platform) {
                  final platformId = (platform['id'] as String? ?? platform['id']?.toString() ?? '').trim();
                  if (platformId.isEmpty) return const SizedBox.shrink();
                  return Expanded(
                    child: _buildPlatformCard(
                      platform,
                      _selectedPlatform == platformId,
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 32),
              
              // Divider
              Divider(
                color: AppTheme.lightGray,
                thickness: 1,
              ),
              const SizedBox(height: 24),
              
              // Required Account Data Section
              Row(
                children: [
                  const Icon(
                    Icons.account_circle,
                    color: AppTheme.textWhite,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'بيانات الحساب المطلوبة',
                    style: TextStyle(
                      color: AppTheme.textWhite,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              // Account ID Input
              TextField(
                controller: _accountIdController,
                style: const TextStyle(color: AppTheme.textWhite),
                decoration: InputDecoration(
                  filled: true,
                  fillColor: AppTheme.darkGray,
                  hintText: 'أدخل رقم الحساب المعرف (ID)',
                  hintStyle: const TextStyle(color: AppTheme.textGray),
                  prefixIcon: const Icon(
                    Icons.badge,
                    color: AppTheme.textGray,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: AppTheme.lightGray),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: AppTheme.lightGray),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(
                      color: AppTheme.neonBlue,
                      width: 2,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              
              // Security Note
              Row(
                children: [
                  const Icon(
                    Icons.lock,
                    color: AppTheme.neonGreen,
                    size: 16,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    'يتم تأمين الاتصال باستخدام بروتوكول SSL المشفر.',
                    style: TextStyle(
                      color: AppTheme.textGray,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              
              // Continue Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _continue,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.neonBlue,
                    foregroundColor: AppTheme.primaryBlack,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text(
                        'متابعة',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Icon(
                        isArabic ? Icons.arrow_back : Icons.arrow_forward,
                        size: 20,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              
              // Post-Continue Actions Section
              Row(
                children: [
                  const Icon(
                    Icons.info_outline,
                    color: AppTheme.textWhite,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'الإجراء بعد المتابعة:',
                    style: TextStyle(
                      color: AppTheme.textWhite,
                      fontSize: 16,
                            fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Padding(
                padding: const EdgeInsets.only(right: 28),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '• ',
                          style: TextStyle(color: AppTheme.textWhite),
                        ),
                        Expanded(
                          child: Text(
                            'ربط الحساب بمنصة التنفيذ المختارة.',
                            style: TextStyle(
                              color: AppTheme.textGray,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          '• ',
                          style: TextStyle(color: AppTheme.textWhite),
                        ),
                        Expanded(
                          child: Text(
                            'تهيئة بيئة التحليل وفق إعدادات المنصة.',
                            style: TextStyle(
                              color: AppTheme.textGray,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),
              
              // Disclaimer
              Center(
                child: Text(
                  'تنويه: لا يتم تنفيذ أي صفقات مالية داخل التطبيق النظام يقدم أدوات تحليلية فقط.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: AppTheme.textGray,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        ),
                ),
    );
  }
}
