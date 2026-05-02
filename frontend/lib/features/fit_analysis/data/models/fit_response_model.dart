import '../../domain/entities/fit_result.dart';

class FitResponseModel extends FitResult {
  FitResponseModel({
    required super.recommendedSize,
    required super.fitClassification,
    required super.confidence,
  });

  factory FitResponseModel.fromJson(Map<String, dynamic> json) {
    return FitResponseModel(
      recommendedSize: json['recommended_size'] as String? ?? '-',
      fitClassification: json['fit_classification'] as String? ?? 'Unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
