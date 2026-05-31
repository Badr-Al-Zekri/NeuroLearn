import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/core/api/api_client.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';

final selectedDocumentProvider = StateProvider<DocumentMetadata?>((ref) => null);

final uploadControllerProvider = StateNotifierProvider<UploadController, AsyncValue<DocumentMetadata?>>((ref) {
  return UploadController(ref);
});

class UploadController extends StateNotifier<AsyncValue<DocumentMetadata?>> {
  UploadController(this._ref) : super(const AsyncData(null));
  final Ref _ref;

  Future<void> uploadText({required String title, required String text}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final document = await _ref.read(apiClientProvider).uploadText(title: title, text: text);
      _ref.read(selectedDocumentProvider.notifier).state = document;
      return document;
    });
  }

  Future<void> uploadPdf({required String title, required String filename, required Uint8List bytes}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final document = await _ref.read(apiClientProvider).uploadPdf(title: title, filename: filename, bytes: bytes);
      _ref.read(selectedDocumentProvider.notifier).state = document;
      return document;
    });
  }
}

final summaryProvider = FutureProvider.autoDispose.family<SummaryResult, String>((ref, documentId) {
  return ref.watch(apiClientProvider).summarize(documentId);
});

final quizProvider = FutureProvider.autoDispose.family<QuizResult, String>((ref, documentId) {
  return ref.watch(apiClientProvider).generateQuiz(documentId);
});

final chatControllerProvider = StateNotifierProvider<ChatController, AsyncValue<List<ChatMessage>>>((ref) {
  return ChatController(ref);
});

class ChatController extends StateNotifier<AsyncValue<List<ChatMessage>>> {
  ChatController(this._ref) : super(const AsyncData([]));
  final Ref _ref;

  Future<bool> send(String message) async {
    final document = _ref.read(selectedDocumentProvider);
    if (document == null || message.trim().isEmpty) {
      return false;
    }

    final current = [...state.valueOrNull ?? const <ChatMessage>[], ChatMessage(role: 'user', content: message.trim())];
    state = AsyncData(current);
    state = const AsyncLoading<List<ChatMessage>>().copyWithPrevious(AsyncData(current));
    final result = await AsyncValue.guard(() async {
      final answer = await _ref.read(apiClientProvider).chat(document.documentId, message.trim(), current);
      return [...current, ChatMessage(role: 'assistant', content: answer.answer)];
    });
    state = result;
    return result.hasValue;
  }

  void reset() {
    state = const AsyncData([]);
  }
}
