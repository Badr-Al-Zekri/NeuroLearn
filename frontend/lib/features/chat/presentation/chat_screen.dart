import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/widgets/empty_state.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
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
      return const Center(child: EmptyState(title: 'Chat needs context', message: 'Upload material before asking document-aware questions.'));
    }
    final chat = ref.watch(chatControllerProvider);
    final messages = chat.valueOrNull ?? const <ChatMessage>[];
    return Padding(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SectionHeader(title: 'AI chat', subtitle: 'Grounded in ${document.title}'),
          const SizedBox(height: 20),
          Expanded(
            child: GlassPanel(
              padding: const EdgeInsets.all(0),
              child: Column(
                children: [
                  Expanded(
                    child: messages.isEmpty
                        ? const Center(
                            child: EmptyState(
                              title: 'Ask a study question',
                              message: 'Try asking for examples, simpler explanations, likely exam prompts, or weak spots.',
                              actionLabel: 'Upload new content',
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.all(18),
                            itemCount: messages.length + (chat.isLoading ? 1 : 0),
                            itemBuilder: (context, index) {
                              if (index >= messages.length) {
                                return const _TypingBubble();
                              }
                              return _MessageBubble(message: messages[index]);
                            },
                          ),
                  ),
                  if (chat.hasError) Padding(padding: const EdgeInsets.fromLTRB(18, 0, 18, 12), child: ErrorBanner(message: chat.error.toString())),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: const BoxDecoration(border: Border(top: BorderSide(color: border))),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            minLines: 1,
                            maxLines: 4,
                            decoration: const InputDecoration(hintText: 'Ask about the uploaded content...'),
                            onSubmitted: (_) => _send(),
                          ),
                        ),
                        const SizedBox(width: 10),
                        IconButton.filled(
                          style: IconButton.styleFrom(backgroundColor: accent, foregroundColor: const Color(0xFF05201D), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
                          onPressed: chat.isLoading ? null : _send,
                          icon: const Icon(Icons.send),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) {
      return;
    }
    _controller.clear();
    ref.read(chatControllerProvider.notifier).send(text);
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
          color: user ? accent.withValues(alpha: 0.16) : const Color(0xFF111827),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: user ? accent.withValues(alpha: 0.45) : border),
        ),
        child: MarkdownBody(
          data: message.content,
          styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
            p: const TextStyle(color: Color(0xFFE5ECFF), height: 1.45),
          ),
        ),
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  const _TypingBubble();

  @override
  Widget build(BuildContext context) {
    return const Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: EdgeInsets.only(bottom: 12),
        child: Chip(
          avatar: SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2)),
          label: Text('NeuroLearn is thinking'),
        ),
      ),
    );
  }
}
