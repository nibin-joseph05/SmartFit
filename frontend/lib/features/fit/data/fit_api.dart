import 'package:dio/dio.dart';

class FitApi {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: "http://10.0.2.2:8000", 
  ));

  Future<Map<String, dynamic>> getSize(Map<String, dynamic> data) async {
    final response = await _dio.post('/size/recommend', data: data);
    return response.data;
  }
}