

"""EXAMPLE"""
# @pytest.mark.parametrize(
#     "a, b, expected_status, expected_result",
#     [
#         (5, 10, 200, 15),
#         (-8, -3, 200, -11),
#         (0, 7, 200, 7),
#         ("a", 10, 422, None),  # Ошибка валидации: строка вместо числа
#         (3, None, 422, None)   # Отсутствует параметр b
#     ]
# )
# async def test_calculate_sum_params(a, b, expected_status, expected_result, client):
#     params = {"a": a}
#     if b is not None:
#         params["b"] = b
#
#     response = await client.get("/sum/", params=params)
#     assert response.status_code == expected_status
#     if expected_status == 200:
#         assert response.json() == {"result": expected_result}
"""EXAMPLE"""


"""MOCK EXAMPLE"""
# import unittest
# from fastapi.testclient import TestClient
# from main import app
# from unittest.mock import patch, MagicMock
#
# client = TestClient(app)
#
#
# class TestMain(unittest.TestCase):
#
#     @patch("main.fetch_data_from_api")
#     @patch("main.process_data")
#     def test_get_and_process_data(self, mock_process_data, mock_fetch_data):
#         # Подготавливаем мокированные данные
#         mock_response = {"key": "value"}
#         mock_processed_data = {"KEY": "VALUE"}
#
#         # Настраиваем поведение моков
#         mock_fetch_data.return_value = mock_response
#         mock_process_data.return_value = mock_processed_data
#
#         # Выполняем запрос
#         response = client.get("/data/")
#
#         # Проверяем вызовы функций
#         mock_fetch_data.assert_called_once()
#         mock_process_data.assert_called_once_with(mock_response)
#
#         # Проверяем ответ API
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json(), mock_processed_data)
"""MOCK EXAMPLE"""
