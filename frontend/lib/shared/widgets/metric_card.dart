import 'package:flutter/material.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';

class MetricCard extends StatelessWidget {
  const MetricCard({super.key, required this.label, required this.value, required this.icon, required this.color});
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return GlassPanel(
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(color: color.withValues(alpha: 0.14), borderRadius: BorderRadius.circular(8)),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900)),
                Text(label, style: const TextStyle(color: Color(0xFF9CA8C7))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
