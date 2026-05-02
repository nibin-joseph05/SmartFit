import '../../domain/entities/fit_result.dart';

class FitResponseModel extends FitResult {
  FitResponseModel({
    required super.generatedImageUrl,
    required super.message,
    required super.confidence,
  });

  factory FitResponseModel.fromJson(Map<String, dynamic> json) {
    return FitResponseModel(
      generatedImageUrl: json['generated_image_url'] as String? ?? '',
      message: json['message'] as String? ?? 'Completed',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
