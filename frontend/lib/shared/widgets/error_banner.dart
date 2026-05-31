import 'package:flutter/material.dart';
import 'package:neurolearn_ai/app/theme.dart';

class ErrorBanner extends StatelessWidget {
  const ErrorBanner({super.key, required this.message, this.actionLabel, this.onAction});
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: danger.withValues(alpha: 0.12),
        border: Border.all(color: danger.withValues(alpha: 0.42)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Wrap(
        crossAxisAlignment: WrapCrossAlignment.center,
        spacing: 10,
        runSpacing: 8,
        children: [
          const Icon(Icons.error_outline, color: danger, size: 20),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: Text(message, style: const TextStyle(height: 1.4)),
          ),
          if (actionLabel != null && onAction != null)
            TextButton(
              onPressed: onAction,
              child: Text(actionLabel!),
            ),
        ],
      ),
    );
  }
}
