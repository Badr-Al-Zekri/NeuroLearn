import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/loading_skeleton.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class QuizScreen extends ConsumerStatefulWidget {
  const QuizScreen({super.key});

  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  final Map<String, int> _answers = {};

  @override
  Widget build(BuildContext context) {
    final document = ref.watch(selectedDocumentProvider);
    if (document == null) {
      return const Center(child: EmptyState(title: 'No quiz yet', message: 'Upload content first, then NeuroLearn will generate practice questions.'));
    }
    final quiz = ref.watch(quizProvider(document.documentId));
    return SingleChildScrollView(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeader(title: 'Adaptive quiz', subtitle: document.title),
          const SizedBox(height: 20),
          quiz.when(
            loading: () => const GlassPanel(child: LoadingSkeleton(lines: 8)),
            error: (error, _) => ErrorBanner(message: error.toString()),
            data: (data) {
              final answered = _answers.length;
              final correct = data.questions.where((q) => _answers[q.id] == q.correctIndex).length;
              return Column(
                children: [
                  GlassPanel(
                    child: Row(
                      children: [
                        Expanded(child: Text(data.title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900))),
                        Text('$correct / $answered correct', style: const TextStyle(color: accent, fontWeight: FontWeight.w900)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  for (final question in data.questions) ...[
                    _QuizCard(
                      question: question,
                      selected: _answers[question.id],
                      onSelected: (index) => setState(() => _answers[question.id] = index),
                    ),
                    const SizedBox(height: 14),
                  ],
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}

class _QuizCard extends StatelessWidget {
  const _QuizCard({required this.question, required this.selected, required this.onSelected});
  final QuizQuestion question;
  final int? selected;
  final ValueChanged<int> onSelected;

  @override
  Widget build(BuildContext context) {
    final answered = selected != null;
    return GlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: accentBlue.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)),
                child: Text(question.difficulty.toUpperCase(), style: const TextStyle(color: accentBlue, fontSize: 12, fontWeight: FontWeight.w900)),
              ),
              const Spacer(),
              if (answered)
                Icon(selected == question.correctIndex ? Icons.check_circle : Icons.cancel, color: selected == question.correctIndex ? accent : danger),
            ],
          ),
          const SizedBox(height: 14),
          Text(question.question, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800, height: 1.35)),
          const SizedBox(height: 14),
          for (var index = 0; index < question.options.length; index++)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _OptionTile(
                label: question.options[index],
                selected: selected == index,
                correct: answered && index == question.correctIndex,
                wrong: answered && selected == index && index != question.correctIndex,
                onTap: () => onSelected(index),
              ),
            ),
          if (answered) ...[
            const SizedBox(height: 8),
            Text(question.explanation, style: const TextStyle(color: Color(0xFFB8C2DD), height: 1.45)),
          ],
        ],
      ),
    );
  }
}

class _OptionTile extends StatelessWidget {
  const _OptionTile({required this.label, required this.selected, required this.correct, required this.wrong, required this.onTap});
  final String label;
  final bool selected;
  final bool correct;
  final bool wrong;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = correct ? accent : wrong ? danger : selected ? accentBlue : border;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color.withValues(alpha: correct || wrong || selected ? 0.12 : 0.04),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color),
        ),
        child: Row(
          children: [
            Icon(correct ? Icons.check_circle_outline : wrong ? Icons.cancel_outlined : Icons.radio_button_unchecked, size: 18, color: color),
            const SizedBox(width: 10),
            Expanded(child: Text(label, style: const TextStyle(height: 1.35))),
          ],
        ),
      ),
    );
  }
}
