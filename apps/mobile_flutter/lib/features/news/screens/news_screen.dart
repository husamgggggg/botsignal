import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/services/news_service.dart';
import '../../../../core/providers/auth_provider.dart';
import '../widgets/news_card.dart';
import '../../home/widgets/top_status_bar.dart';
import '../../home/widgets/bottom_nav_bar.dart';

class NewsScreen extends ConsumerStatefulWidget {
  const NewsScreen({super.key});

  @override
  ConsumerState<NewsScreen> createState() => _NewsScreenState();
}

class _NewsScreenState extends ConsumerState<NewsScreen> {
  List<dynamic> _news = [];
  bool _loading = true;
  String? _error;
  int _selectedNavIndex = 1; // News is index 1

  @override
  void initState() {
    super.initState();
    _loadNews();
  }

  Future<void> _loadNews() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final apiService = ref.read(apiServiceProvider);
      final newsService = NewsService(apiService);
      
      // Try to load from API
      try {
        final news = await newsService.getNews();
        if (news.isNotEmpty) {
          setState(() {
            _news = news;
            _loading = false;
          });
          return;
        }
      } catch (e) {
        // If API fails, load mock data
      }
      
      // Load mock news for preview
      _loadMockNews();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  void _loadMockNews() {
    setState(() {
      _news = [
        {
          'id': '1',
          'name': 'Non-Farm Payrolls',
          'nameAr': 'مؤشر التوظيف الأمريكي',
          'impact': 3, // 3 stars (high impact)
          'time': '14:30 GMT',
          'previous': '150K',
          'forecast': '180K',
          'actual': '175K',
          'currency': 'USD',
        },
        {
          'id': '2',
          'name': 'CPI (Consumer Price Index)',
          'nameAr': 'مؤشر أسعار المستهلك',
          'impact': 3, // 3 stars
          'time': '13:30 GMT',
          'previous': '3.2%',
          'forecast': '3.5%',
          'actual': '3.4%',
          'currency': 'USD',
        },
        {
          'id': '3',
          'name': 'Interest Rate Decision',
          'nameAr': 'قرار سعر الفائدة',
          'impact': 3, // 3 stars
          'time': '19:00 GMT',
          'previous': '5.25%',
          'forecast': '5.50%',
          'actual': null, // Not released yet
          'currency': 'USD',
        },
        {
          'id': '4',
          'name': 'GDP Growth Rate',
          'nameAr': 'معدل نمو الناتج المحلي',
          'impact': 2, // 2 stars (medium impact)
          'time': '13:00 GMT',
          'previous': '2.1%',
          'forecast': '2.3%',
          'actual': '2.2%',
          'currency': 'EUR',
        },
        {
          'id': '5',
          'name': 'Unemployment Rate',
          'nameAr': 'معدل البطالة',
          'impact': 2, // 2 stars
          'time': '09:00 GMT',
          'previous': '3.7%',
          'forecast': '3.8%',
          'actual': '3.6%',
          'currency': 'GBP',
        },
      ];
      _loading = false;
    });
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
              
              // News List
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
                                  'حدث خطأ في تحميل الأخبار',
                                  style: const TextStyle(
                                    color: Color(0xFFB0B7C3),
                                    fontSize: 16,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: _loadNews,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF347AF0),
                                    foregroundColor: Colors.white,
                                  ),
                                  child: const Text('إعادة المحاولة'),
                                ),
                              ],
                            ),
                          )
                        : _news.isEmpty
                            ? Center(
                                child: Text(
                                  'لا توجد أخبار متاحة حالياً',
                                  style: const TextStyle(
                                    color: Color(0xFFB0B7C3),
                                    fontSize: 16,
                                  ),
                                ),
                              )
                            : RefreshIndicator(
                                onRefresh: _loadNews,
                                color: const Color(0xFF347AF0),
                                child: ListView.builder(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  itemCount: _news.length,
                                  itemBuilder: (context, index) {
                                    final newsItem = _news[index];
                                    return Padding(
                                      padding: const EdgeInsets.only(bottom: 16),
                                      child: NewsCard(news: newsItem),
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

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedNavIndex = index;
    });

    switch (index) {
      case 0:
        context.go('/home');
        break;
      case 1:
        // Already on news page
        break;
      case 2:
        // Performance page - implement later
        break;
      case 3:
        context.push('/settings');
        break;
    }
  }
}

