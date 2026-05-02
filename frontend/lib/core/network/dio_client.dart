import 'package:dio/dio.dart';

class DioClient {
  final Dio dio;

  DioClient() : dio = Dio(
    BaseOptions(
      baseUrl: 'http://10.53.244.175:8000/api/v1', 
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  ) {
    dio.interceptors.add(LogInterceptor(responseBody: true, requestBody: true));
  }
}
