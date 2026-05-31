import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/providers/learning_session_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class TutorScreen extends ConsumerStatefulWidget {
  const TutorScreen({super.key});

  @override
  ConsumerState<TutorScreen> createState() => _TutorScreenState();
}

class _TutorScreenState extends ConsumerState<TutorScreen> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final document = ref.watch(selectedDocumentProvider);
    if (document == null) {
      return const Center(
        child: EmptyState(
          title: 'Choose what to study first',
          message: 'Your tutor will stay focused on the material you choose for today.',
          actionLabel: 'Choose material',
        ),
      );
    }
    final messagesState = ref.watch(chatControllerProvider);
    final messages = messagesState.valueOrNull ?? const <ChatMessage>[];
    final compact = MediaQuery.sizeOf(context).width < 600;
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: compact ? 12 : 20, vertical: compact ? 12 : 20),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 880),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SectionHeader(title: 'Tutor', subtitle: 'Make sense of ${document.title}'),
              const SizedBox(height: 14),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 9),
                decoration: BoxDecoration(color: surface, borderRadius: BorderRadius.circular(8), border: Border.all(color: border)),
                child: const Row(
                  children: [
                    Icon(Icons.verified_outlined, size: 16, color: accent),
                    SizedBox(width: 8),
                    Expanded(child: Text('Your explanation stays connected to today\'s material.', style: TextStyle(fontSize: 13, color: Color(0xFFB5C1C4)))),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: GlassPanel(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      Expanded(
                        child: messages.isEmpty
                            ? _TutorWelcome(onPrompt: _sendPrompt, enabled: !messagesState.isLoading)
                            : ListView.builder(
                                padding: const EdgeInsets.all(18),
                                itemCount: messages.length + (messagesState.isLoading ? 1 : 0),
                                itemBuilder: (context, index) {
                                  if (index >= messages.length) {
                                    return const _ThinkingBubble();
                                  }
                                  return _MessageBubble(message: messages[index]);
                                },
                              ),
                      ),
                      if (messages.isNotEmpty && !messagesState.isLoading)
                        _FollowUpPrompts(onPrompt: _sendPrompt, enabled: true),
                      if (messagesState.hasError)
                        const Padding(
                          padding: EdgeInsets.fromLTRB(18, 0, 18, 12),
                          child: ErrorBanner(message: 'That explanation did not arrive. Ask again when you are ready.'),
                        ),
                      Padding(
                        padding: const EdgeInsets.fromLTRB(14, 8, 14, 14),
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                controller: _controller,
                                minLines: 1,
                                maxLines: 3,
                                decoration: const InputDecoration(hintText: 'What would help this click?'),
                                onSubmitted: (_) {
                                  if (!messagesState.isLoading) {
                                    _send();
                                  }
                                },
                              ),
                            ),
                            const SizedBox(width: 10),
                            IconButton.filled(
                              tooltip: 'Send question',
                              style: IconButton.styleFrom(
                                backgroundColor: accent,
                                foregroundColor: const Color(0xFF05201D),
                                minimumSize: const Size(48, 48),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                              ),
                              onPressed: messagesState.isLoading ? null : _send,
                              icon: const Icon(Icons.arrow_upward),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              if (messages.isNotEmpty) ...[
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size.fromHeight(50),
                      foregroundColor: accent,
                      side: const BorderSide(color: border),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                    onPressed: () => context.go('/practice'),
                    icon: const Icon(Icons.arrow_forward),
                    label: const Text('I am ready for a quick review'),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _sendPrompt(String text) {
    _controller.text = text;
    _send();
  }

  Future<void> _send() async {
    if (ref.read(chatControllerProvider).isLoading) {
      return;
    }
    final text = _controller.text.trim();
    if (text.isEmpty) {
      return;
    }
    _controller.clear();
    final answered = await ref.read(chatControllerProvider.notifier).send(text);
    if (answered) {
      await ref.read(activeStudySessionProvider.notifier).recordTutorInteraction();
    }
  }
}

class _TutorWelcome extends StatelessWidget {
  const _TutorWelcome({required this.onPrompt, required this.enabled});
  final ValueChanged<String> onPrompt;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.psychology_alt_outlined, color: accent, size: 42),
            const SizedBox(height: 14),
            Text('Let us make one idea clear', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900)),
            const SizedBox(height: 8),
            const Text('Begin with a question below. When it settles, a short review will help it stay.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF99A6AB), height: 1.4)),
            const SizedBox(height: 18),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                _PromptChip(label: 'Explain the key idea simply', onTap: onPrompt, enabled: enabled),
                _PromptChip(label: 'What must I remember today?', onTap: onPrompt, enabled: enabled),
                _PromptChip(label: 'Show one clear example', onTap: onPrompt, enabled: enabled),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _FollowUpPrompts extends StatelessWidget {
  const _FollowUpPrompts({required this.onPrompt, required this.enabled});
  final ValueChanged<String> onPrompt;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(14, 10, 14, 4),
      decoration: const BoxDecoration(border: Border(top: BorderSide(color: border))),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Choose your next step', style: TextStyle(color: Color(0xFF99A6AB), fontSize: 12, fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _PromptChip(label: 'Explain that more simply', onTap: onPrompt, enabled: enabled),
              _PromptChip(label: 'What should I remember?', onTap: onPrompt, enabled: enabled),
              _PromptChip(label: 'Give me a quick check', onTap: onPrompt, enabled: enabled),
            ],
          ),
        ],
      ),
    );
  }
}

class _PromptChip extends StatelessWidget {
  const _PromptChip({required this.label, required this.onTap, required this.enabled});
  final String label;
  final ValueChanged<String> onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    return ActionChip(
      label: Text(label, style: const TextStyle(fontSize: 13)),
      onPressed: enabled ? () => onTap(label) : null,
      backgroundColor: surface,
      side: const BorderSide(color: border),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  const _MessageBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final user = message.role == 'user';
    return Align(
      alignment: user ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 720),
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: user ? accent.withValues(alpha: 0.10) : surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: user ? accent.withValues(alpha: 0.28) : border),
        ),
        child: MarkdownBody(data: message.content, styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(p: const TextStyle(color: Color(0xFFE5ECFF), height: 1.45))),
      ),
    );
  }
}

class _ThinkingBubble extends StatelessWidget {
  const _ThinkingBubble();

  @override
  Widget build(BuildContext context) {
    return const Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.only(bottom: 12),
        child: Chip(
          avatar: SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)),
          label: Text('Finding a clear explanation'),
        ),
      ),
    );
  }
}
