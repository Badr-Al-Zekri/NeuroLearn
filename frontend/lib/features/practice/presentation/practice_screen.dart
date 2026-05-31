import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/providers/learning_session_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/loading_skeleton.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class PracticeScreen extends ConsumerStatefulWidget {
  const PracticeScreen({super.key});

  @override
  ConsumerState<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends ConsumerState<PracticeScreen> {
  final Map<String, int> _answers = {};
  bool _completionTracked = false;
  bool _recordingAnswer = false;
  String? _recordingError;
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    final document = ref.watch(selectedDocumentProvider);
    if (document == null) {
      return const Center(
        child: EmptyState(
          title: 'Choose material for a quick review',
          message: 'A few gentle questions will help today\'s learning settle in.',
          actionLabel: 'Choose material',
        ),
      );
    }
    final quiz = ref.watch(quizProvider(document.documentId));
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 700),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionHeader(title: 'Quick review', subtitle: 'One question at a time. Keep what you learned close.'),
              const SizedBox(height: 18),
              quiz.when(
            loading: () => const GlassPanel(child: LoadingSkeleton(lines: 8)),
            error: (error, _) => ErrorBanner(
              message: 'We could not prepare your quick review. Please try again.',
              actionLabel: 'Try again',
              onAction: () => ref.invalidate(quizProvider(document.documentId)),
            ),
            data: (data) {
              final questions = data.questions.take(5).toList();
              if (questions.isEmpty) {
                return const GlassPanel(
                  child: Text(
                    'There is nothing to review yet. Return to Tutor for one clear explanation first.',
                    style: TextStyle(color: Color(0xFFC7D1D3), height: 1.45),
                  ),
                );
              }
              final correct = questions.where((q) => _answers[q.id] == q.correctIndex).length;
              final complete = _currentIndex >= questions.length;
              final question = complete ? null : questions[_currentIndex];
              final answered = question != null && _answers.containsKey(question.id);
              final completedSteps = complete ? questions.length : _currentIndex + (answered ? 1 : 0);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  GlassPanel(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                complete ? 'Review complete' : 'Question ${_currentIndex + 1} of ${questions.length}',
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                              ),
                            ),
                            Text(
                              complete ? '$correct correct' : '${_answers.length} answered',
                              style: const TextStyle(color: accent, fontWeight: FontWeight.w900),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: LinearProgressIndicator(
                            value: completedSteps / questions.length,
                            minHeight: 5,
                            color: accent,
                            backgroundColor: border,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 180),
                    child: complete
                        ? _CompletionCard(
                            key: const ValueKey('completed'),
                            correct: correct,
                            total: questions.length,
                            onContinue: () {
                              if (context.mounted) {
                                context.go('/progress');
                              }
                            },
                          )
                        : Column(
                            key: ValueKey(question!.id),
                            children: [
                              _QuestionCard(
                                question: question,
                                selected: _answers[question.id],
                                onSelect: (index) => _selectAnswer(question, index),
                              ),
                              if (answered) ...[
                                const SizedBox(height: 12),
                                if (_recordingError != null) ...[
                                  const ErrorBanner(
                                    message: 'Your answer is kept here. You can continue with today\'s review.',
                                  ),
                                  const SizedBox(height: 12),
                                ],
                                SizedBox(
                                  width: double.infinity,
                                  child: PrimaryButton(
                                    label: _currentIndex == questions.length - 1 ? 'Finish review' : 'Next question',
                                    icon: Icons.arrow_forward,
                                    loading: _recordingAnswer,
                                    onPressed: () async {
                                      if (_currentIndex == questions.length - 1 && !_completionTracked) {
                                        _completionTracked = true;
                                        await ref.read(activeStudySessionProvider.notifier).completeQuiz(correct, questions.length);
                                      }
                                      if (mounted) {
                                        setState(() => _currentIndex += 1);
                                      }
                                    },
                                  ),
                                ),
                              ],
                            ],
                          ),
                  ),
                ],
              );
            },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _selectAnswer(QuizQuestion question, int index) async {
    if (_answers.containsKey(question.id) || _recordingAnswer) {
      return;
    }
    setState(() {
      _answers[question.id] = index;
      _recordingAnswer = true;
      _recordingError = null;
    });
    try {
      await ref.read(activeStudySessionProvider.notifier).recordQuizAnswer(
            conceptId: question.id,
            conceptName: question.question,
            correct: index == question.correctIndex,
          );
    } catch (_) {
      if (mounted) {
        setState(() => _recordingError = 'recording_failed');
      }
    } finally {
      if (mounted) {
        setState(() => _recordingAnswer = false);
      }
    }
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({required this.question, required this.selected, required this.onSelect});
  final QuizQuestion question;
  final int? selected;
  final ValueChanged<int> onSelect;

  @override
  Widget build(BuildContext context) {
    final answered = selected != null;
    return GlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(question.question, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800, height: 1.35)),
          const SizedBox(height: 14),
          for (var index = 0; index < question.options.length; index++)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _AnswerOption(
                label: question.options[index],
                selected: selected == index,
                correct: answered && index == question.correctIndex,
                wrong: answered && selected == index && index != question.correctIndex,
                onTap: () => onSelect(index),
              ),
            ),
          if (answered) ...[
            const SizedBox(height: 8),
            Text(
              selected == question.correctIndex ? 'That is it. Keep this connection.' : 'Not yet. This quick review helps it stick.',
              style: TextStyle(color: selected == question.correctIndex ? accent : accentBlue, fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 6),
            Text(question.explanation, style: const TextStyle(color: Color(0xFFB8C2DD), height: 1.45)),
          ],
        ],
      ),
    );
  }
}

class _AnswerOption extends StatelessWidget {
  const _AnswerOption({required this.label, required this.selected, required this.correct, required this.wrong, required this.onTap});
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
        duration: const Duration(milliseconds: 160),
        padding: const EdgeInsets.all(13),
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

class _CompletionCard extends StatelessWidget {
  const _CompletionCard({super.key, required this.correct, required this.total, required this.onContinue});
  final int correct;
  final int total;
  final VoidCallback onContinue;

  @override
  Widget build(BuildContext context) {
    return GlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline, color: accent, size: 34),
          const SizedBox(height: 12),
          Text('You completed today\'s review.', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 8),
          Text(
            '$correct of $total correct. You are making steady progress.',
            style: const TextStyle(color: Color(0xFFC7D1D3), height: 1.45),
          ),
          const SizedBox(height: 18),
          SizedBox(
            width: double.infinity,
            child: PrimaryButton(label: 'See today\'s progress', icon: Icons.arrow_forward, onPressed: onContinue),
          ),
        ],
      ),
    );
  }
}
