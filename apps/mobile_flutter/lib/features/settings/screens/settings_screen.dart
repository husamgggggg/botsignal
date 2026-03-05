import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/providers/locale_provider.dart';
import '../../../../core/providers/auth_provider.dart';
import '../../../../core/providers/timezone_provider.dart';
import '../../../../core/services/timezone_service.dart';
import '../../home/widgets/bottom_nav_bar.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  int _selectedNavIndex = 3; // Settings is index 3

  @override
  void initState() {
    super.initState();
    // Load selected country
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(timezoneProvider.notifier).loadCountry();
    });
  }

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedNavIndex = index;
    });

    switch (index) {
      case 0:
        context.go('/home');
        break;
      case 1:
        context.push('/news');
        break;
      case 2:
        // Performance page - implement later
        break;
      case 3:
        // Already on settings page
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context);
    final locale = ref.watch(localeProvider);
    final localeNotifier = ref.read(localeProvider.notifier);
    final selectedCountry = ref.watch(timezoneProvider);
    final timezoneNotifier = ref.read(timezoneProvider.notifier);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: const Color(0xFF0F1115),
        appBar: AppBar(
          title: Text(localizations.settings),
          backgroundColor: const Color(0xFF141821),
        ),
        body: ListView(
          children: [
            ListTile(
              title: const Text(
                'اللغة',
                style: TextStyle(color: Colors.white),
              ),
              subtitle: Text(
                locale.languageCode == 'ar' ? localizations.arabic : localizations.english,
                style: const TextStyle(color: Color(0xFFB0B7C3)),
              ),
              trailing: const Icon(Icons.arrow_forward_ios, color: Color(0xFF8A9099)),
              onTap: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: Text(localizations.language),
                    content: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        ListTile(
                          title: Text(localizations.arabic),
                          leading: Radio<Locale>(
                            value: const Locale('ar'),
                            groupValue: locale,
                            onChanged: (value) {
                              if (value != null) {
                                localeNotifier.setLocale(value);
                                Navigator.pop(context);
                              }
                            },
                          ),
                        ),
                        ListTile(
                          title: Text(localizations.english),
                          leading: Radio<Locale>(
                            value: const Locale('en'),
                            groupValue: locale,
                            onChanged: (value) {
                              if (value != null) {
                                localeNotifier.setLocale(value);
                                Navigator.pop(context);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            const Divider(color: Color.fromRGBO(255, 255, 255, 0.06)),
            ListTile(
              title: const Text(
                'البلد',
                style: TextStyle(color: Colors.white),
              ),
              subtitle: Text(
                selectedCountry ?? 'افتراضي (توقيت الجهاز)',
                style: const TextStyle(color: Color(0xFFB0B7C3)),
              ),
              trailing: const Icon(Icons.arrow_forward_ios, color: Color(0xFF8A9099)),
              onTap: () {
                _showCountryDialog(context, selectedCountry, timezoneNotifier);
              },
            ),
            const Divider(color: Color.fromRGBO(255, 255, 255, 0.06)),
            ListTile(
              title: const Text(
                'تغيير المنصة',
                style: TextStyle(color: Colors.white),
              ),
              trailing: const Icon(Icons.arrow_forward_ios, color: Color(0xFF8A9099)),
              onTap: () {
                context.go('/platform-select');
              },
            ),
            const Divider(color: Color.fromRGBO(255, 255, 255, 0.06)),
            ListTile(
              title: const Text(
                'تسجيل الخروج',
                style: TextStyle(color: Colors.red),
              ),
              trailing: const Icon(Icons.logout, color: Colors.red),
              onTap: () async {
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) {
                  context.go('/platform-select');
                }
              },
            ),
          ],
        ),
        bottomNavigationBar: BottomNavBar(
          selectedIndex: _selectedNavIndex,
          onItemTapped: _onNavItemTapped,
        ),
      ),
    );
  }

  void _showCountryDialog(BuildContext context, String? selectedCountry, TimezoneNotifier notifier) {
    final countries = TimezoneService.getAvailableCountries();
    
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          backgroundColor: const Color(0xFF151922),
          title: const Text(
            'اختر البلد',
            style: TextStyle(color: Colors.white),
          ),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: countries.length,
              itemBuilder: (context, index) {
                final country = countries[index];
                final isSelected = country == selectedCountry;
                
                return ListTile(
                  title: Text(
                    country,
                    style: TextStyle(
                      color: isSelected ? const Color(0xFF347AF0) : Colors.white,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                  leading: Radio<String>(
                    value: country,
                    groupValue: selectedCountry,
                    onChanged: (value) {
                      if (value != null) {
                        notifier.setCountry(value);
                        Navigator.pop(context);
                        setState(() {}); // Refresh UI
                      }
                    },
                    activeColor: const Color(0xFF347AF0),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

