import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/core/config/app_config.dart';
import 'package:neurolearn_ai/core/errors/app_error.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

class ApiClient {
  ApiClient()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppConfig.apiBaseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 45),
          ),
        );

  final Dio _dio;

  Future<DocumentMetadata> uploadText({required String title, required String text}) async {
    return _sendUpload(FormData.fromMap({'title': title, 'text': text}));
  }

  Future<DocumentMetadata> uploadPdf({
    required String title,
    required String filename,
    required Uint8List bytes,
  }) async {
    final data = FormData.fromMap({
      'title': title,
      'file': MultipartFile.fromBytes(bytes, filename: filename),
    });
    return _sendUpload(data);
  }

  Future<DocumentMetadata> _sendUpload(FormData data) async {
    try {
      final response = await _dio.post('/api/documents/upload', data: data);
      return DocumentMetadata.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<SummaryResult> summarize(String documentId) async {
    try {
      final response = await _dio.post('/api/documents/$documentId/summary', data: {});
      return SummaryResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<QuizResult> generateQuiz(String documentId, {int count = 5}) async {
    try {
      final response = await _dio.post('/api/documents/$documentId/quiz', data: {'question_count': count});
      return QuizResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<ChatAnswer> chat(String documentId, String message, List<ChatMessage> history) async {
    try {
      final response = await _dio.post(
        '/api/documents/$documentId/chat',
        data: {'message': message, 'history': history.map((item) => item.toJson()).toList()},
      );
      return ChatAnswer.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<StudySession> startStudySession(String learnerId, List<String> documentIds) async {
    try {
      final response = await _dio.post('/api/learners/$learnerId/sessions', data: {'document_ids': documentIds});
      return StudySession.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<StudySession> recordStudyEvent(
    String learnerId,
    String sessionId, {
    required String eventType,
    String? documentId,
    String? conceptId,
    String? conceptName,
    bool? correct,
    double confidence = 0.6,
  }) async {
    try {
      final response = await _dio.post(
        '/api/learners/$learnerId/sessions/$sessionId/events',
        data: {
          'event_type': eventType,
          'document_id': documentId,
          'concept_id': conceptId,
          'concept_name': conceptName,
          'correct': correct,
          'confidence': confidence,
        },
      );
      return StudySession.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<StudySession> endStudySession(String learnerId, String sessionId) async {
    try {
      final response = await _dio.post('/api/learners/$learnerId/sessions/$sessionId/end');
      return StudySession.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<AdaptiveDecisionSummary> adaptiveDecision(String learnerId) async {
    try {
      final response = await _dio.get('/api/learners/$learnerId/adaptive/decision');
      return AdaptiveDecisionSummary.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  Future<LearnerSnapshot> learnerSnapshot(String learnerId) async {
    try {
      final response = await _dio.get('/api/learners/$learnerId/intelligence');
      return LearnerSnapshot.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (error) {
      throw AppError(_message(error));
    }
  }

  String _message(DioException error) {
    final data = error.response?.data;
    if (data is Map && data['detail'] is String) {
      return data['detail'] as String;
    }
    return 'We could not connect right now. Please try again in a moment.';
  }
}
