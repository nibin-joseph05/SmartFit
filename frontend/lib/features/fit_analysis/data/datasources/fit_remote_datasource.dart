import 'dart:io';
import 'package:dio/dio.dart';
import '../../../../core/network/dio_client.dart';
import '../models/fit_response_model.dart';

class FitRemoteDataSource {
  final DioClient _client;

  FitRemoteDataSource(this._client);

  Future<FitResponseModel> analyzeFit({
    required File personImage,
    required File garmentImage,
    required String garmentType,       
  }) async {
    final formData = FormData.fromMap({
      'person_image':  await MultipartFile.fromFile(personImage.path,  filename: 'person.jpg'),
      'garment_image': await MultipartFile.fromFile(garmentImage.path, filename: 'garment.jpg'),
      'garment_type':  garmentType,      
    });

    final response = await _client.dio.post(
      '/fit/analyze',
      data: formData,
      options: Options(
        receiveTimeout: const Duration(minutes: 2),
        sendTimeout:    const Duration(minutes: 2),
      ),
    );
    return FitResponseModel.fromJson(response.data);
  }
}