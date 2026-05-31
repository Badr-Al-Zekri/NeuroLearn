import 'dart:async';
import 'dart:typed_data';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dropzone/flutter_dropzone.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/app/theme.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/providers/learning_session_provider.dart';
import 'package:neurolearn_ai/shared/widgets/error_banner.dart';
import 'package:neurolearn_ai/shared/widgets/glass_panel.dart';
import 'package:neurolearn_ai/shared/widgets/primary_button.dart';
import 'package:neurolearn_ai/shared/widgets/section_header.dart';

class UploadScreen extends ConsumerStatefulWidget {
  const UploadScreen({super.key});

  @override
  ConsumerState<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends ConsumerState<UploadScreen> {
  final _titleController = TextEditingController(text: 'Neurobiology notes');
  final _textController = TextEditingController();
  DropzoneViewController? _dropzone;
  bool _hovering = false;

  @override
  void dispose() {
    _titleController.dispose();
    _textController.dispose();
    super.dispose();
  }

  Future<void> _uploadPickedPdf() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['pdf'], withData: true);
    final file = result?.files.single;
    if (file?.bytes == null) {
      return;
    }
    await _uploadPdf(file!.name, file.bytes!);
  }

  Future<void> _uploadPdf(String filename, Uint8List bytes) async {
    await ref.read(uploadControllerProvider.notifier).uploadPdf(
          title: _titleController.text.trim().isEmpty ? filename : _titleController.text.trim(),
          filename: filename,
          bytes: bytes,
        );
    await _finishUpload();
  }

  Future<void> _uploadText() async {
    await ref.read(uploadControllerProvider.notifier).uploadText(
          title: _titleController.text.trim().isEmpty ? 'Study notes' : _titleController.text.trim(),
          text: _textController.text.trim(),
        );
    await _finishUpload();
  }

  Future<void> _finishUpload() async {
    final uploaded = ref.read(uploadControllerProvider).valueOrNull;
    if (uploaded == null) {
      return;
    }
    unawaited(ref.read(activeStudySessionProvider.notifier).leaveForNewMaterial());
    ref.read(chatControllerProvider.notifier).reset();
    if (mounted) {
      context.go('/');
    }
  }

  @override
  Widget build(BuildContext context) {
    final uploadState = ref.watch(uploadControllerProvider);
    final isLoading = uploadState.isLoading;
    final canUploadText = _textController.text.trim().split(RegExp(r'\s+')).where((word) => word.isNotEmpty).length >= 20;
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1060),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SectionHeader(
                title: 'Choose today\'s material',
                subtitle: 'Add one readable PDF or paste notes to begin a focused study session.',
              ),
              const SizedBox(height: 20),
              if (uploadState.hasError) ...[
                ErrorBanner(message: uploadState.error.toString()),
                const SizedBox(height: 14),
              ],
              LayoutBuilder(
                builder: (context, constraints) {
                  final wide = constraints.maxWidth > 860;
                  return Flex(
                    direction: wide ? Axis.horizontal : Axis.vertical,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (wide)
                        Expanded(
                          flex: 5,
                          child: _DropArea(
                            hovering: _hovering,
                            loading: isLoading,
                            onPick: _uploadPickedPdf,
                            onCreated: (c) => _dropzone = c,
                            onHover: () => setState(() => _hovering = true),
                            onLeave: () => setState(() => _hovering = false),
                            onDropFile: _handleDrop,
                          ),
                        )
                      else
                        _DropArea(
                          hovering: _hovering,
                          loading: isLoading,
                          onPick: _uploadPickedPdf,
                          onCreated: (c) => _dropzone = c,
                          onHover: () => setState(() => _hovering = true),
                          onLeave: () => setState(() => _hovering = false),
                          onDropFile: _handleDrop,
                        ),
                      SizedBox(width: wide ? 18 : 0, height: wide ? 0 : 18),
                      if (wide)
                        Expanded(
                          flex: 6,
                          child: _TextUploadCard(
                            titleController: _titleController,
                            textController: _textController,
                            loading: isLoading,
                            canUpload: canUploadText,
                            onTextChanged: (_) => setState(() {}),
                            onUpload: _uploadText,
                          ),
                        )
                      else
                        _TextUploadCard(
                          titleController: _titleController,
                          textController: _textController,
                          loading: isLoading,
                          canUpload: canUploadText,
                          onTextChanged: (_) => setState(() {}),
                          onUpload: _uploadText,
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

  Future<void> _handleDrop(dynamic event) async {
    final controller = _dropzone;
    if (controller == null) {
      return;
    }
    setState(() => _hovering = false);
    final filename = await controller.getFilename(event);
    final bytes = await controller.getFileData(event);
    await _uploadPdf(filename, bytes);
  }
}

class _DropArea extends StatelessWidget {
  const _DropArea({
    required this.hovering,
    required this.loading,
    required this.onPick,
    required this.onCreated,
    required this.onHover,
    required this.onLeave,
    required this.onDropFile,
  });

  final bool hovering;
  final bool loading;
  final VoidCallback onPick;
  final ValueChanged<DropzoneViewController> onCreated;
  final VoidCallback onHover;
  final VoidCallback onLeave;
  final ValueChanged<dynamic> onDropFile;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 360,
      child: Stack(
        children: [
          DropzoneView(
            onCreated: onCreated,
            onHover: loading ? null : onHover,
            onLeave: onLeave,
            onDropFile: loading ? null : onDropFile,
          ),
          IgnorePointer(
            child: GlassPanel(
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                width: double.infinity,
                height: double.infinity,
                decoration: BoxDecoration(
                  color: hovering ? accent.withValues(alpha: 0.08) : const Color(0xFF111827),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: hovering ? accent : border, width: 1.4),
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.cloud_upload_outlined, size: 58, color: accent),
                    SizedBox(height: 16),
                    Text('Drop a PDF here', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
                    SizedBox(height: 8),
                    Text('or click to select a readable PDF', style: TextStyle(color: Color(0xFF9CA8C7))),
                  ],
                ),
              ),
            ),
          ),
          Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 34),
              child: FilledButton.icon(
                style: FilledButton.styleFrom(
                  backgroundColor: accent,
                  foregroundColor: const Color(0xFF05201D),
                  minimumSize: const Size(0, 52),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: loading ? null : onPick,
                icon: const Icon(Icons.folder_open),
                label: const Text('Select PDF'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TextUploadCard extends StatelessWidget {
  const _TextUploadCard({
    required this.titleController,
    required this.textController,
    required this.loading,
    required this.canUpload,
    required this.onTextChanged,
    required this.onUpload,
  });
  final TextEditingController titleController;
  final TextEditingController textController;
  final bool loading;
  final bool canUpload;
  final ValueChanged<String> onTextChanged;
  final VoidCallback onUpload;

  @override
  Widget build(BuildContext context) {
    return GlassPanel(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Paste notes', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900)),
          const SizedBox(height: 14),
          TextField(controller: titleController, decoration: const InputDecoration(labelText: 'Document title')),
          const SizedBox(height: 12),
          TextField(
            controller: textController,
            minLines: 9,
            maxLines: 14,
            decoration: const InputDecoration(hintText: 'Paste lecture notes, article sections, or textbook excerpts...'),
            onChanged: onTextChanged,
          ),
          const SizedBox(height: 10),
          Text(
            canUpload ? 'Ready for today\'s session.' : 'Add at least 20 words to prepare a useful session.',
            style: const TextStyle(color: Color(0xFF99A6AB), fontSize: 13),
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerRight,
            child: PrimaryButton(
              label: 'Prepare today\'s session',
              icon: Icons.arrow_forward,
              loading: loading,
              onPressed: canUpload ? onUpload : null,
            ),
          ),
        ],
      ),
    );
  }
}
