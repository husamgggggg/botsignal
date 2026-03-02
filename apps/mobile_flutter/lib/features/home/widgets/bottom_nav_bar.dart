import 'package:flutter/material.dart';

class BottomNavBar extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onItemTapped;

  const BottomNavBar({
    super.key,
    required this.selectedIndex,
    required this.onItemTapped,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 70,
      decoration: const BoxDecoration(
        color: Color(0xFF141821),
        border: Border(
          top: BorderSide(
            color: Color.fromRGBO(255, 255, 255, 0.06),
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildNavItem(
            icon: Icons.bar_chart,
            label: 'الإشارات',
            index: 0,
            isSelected: selectedIndex == 0,
          ),
          _buildNavItem(
            icon: Icons.newspaper_outlined,
            label: 'الأخبار',
            index: 1,
            isSelected: selectedIndex == 1,
          ),
                _buildNavItem(
                  icon: Icons.notifications,
                  label: 'الإشعارات',
                  index: 2,
                  isSelected: selectedIndex == 2,
                ),
          _buildNavItem(
            icon: Icons.settings_outlined,
            label: 'الإعدادات',
            index: 3,
            isSelected: selectedIndex == 3,
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem({
    required IconData icon,
    required String label,
    required int index,
    required bool isSelected,
  }) {
    final color = isSelected ? const Color(0xFF347AF0) : const Color(0xFF8A9099);

    return Expanded(
      child: InkWell(
        onTap: () => onItemTapped(index),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: color,
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

