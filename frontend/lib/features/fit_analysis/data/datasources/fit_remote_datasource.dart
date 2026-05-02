import 'dart:io';
import 'package:dio/dio.dart';
import '../../../../core/network/dio_client.dart';
import '../models/fit_response_model.dart';

class FitRemoteDataSource {
  final DioClient _client;

  FitRemoteDataSource(this._client);

  Future<FitResponseModel> analyzeFit({
    required double height,
    required double weight,
    required String dressType,
    required File imageFile,
  }) async {
    final formData = FormData.fromMap({
      'height': height,
      'weight': weight,
      'dress_type': dressType,
      'image': await MultipartFile.fromFile(imageFile.path, filename: 'upload.jpg'),
    });

    final response = await _client.dio.post('/fit/analyze', data: formData);
    return FitResponseModel.fromJson(response.data);
  }
}
