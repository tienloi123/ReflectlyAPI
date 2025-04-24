from enum import Enum
from starlette import status


class AppStatus(Enum):
    SUCCESS = status.HTTP_200_OK, 'SUCCESS', 'Thành công!'

    ERROR_400_BAD_REQUEST = status.HTTP_400_BAD_REQUEST, 'BAD_REQUEST', 'Yêu cầu không hợp lệ.'
    ERROR_400_INVALID_DATA = status.HTTP_400_BAD_REQUEST, 'INVALID_DATA', 'Dữ liệu vào không hợp lệ: {description}'

    ERROR_500_INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR, 'INTERNAL_SERVER_ERROR', ('Đã xảy ra lỗi '
                                                                                                       'máy chủ nội '
                                                                                                       'bộ. Đây là '
                                                                                                       'vấn đề từ '
                                                                                                       'phía chúng '
                                                                                                       'tôi, '
                                                                                                       'và chúng tôi '
                                                                                                       'đang tích cực '
                                                                                                       'làm việc để '
                                                                                                       'giải quyết '
                                                                                                       'nó. Chúng tôi '
                                                                                                       'xin lỗi vì '
                                                                                                       'bất kỳ sự bất '
                                                                                                       'tiện nào điều '
                                                                                                       'này có thể đã '
                                                                                                       'gây ra. Nếu '
                                                                                                       'bạn cần hỗ '
                                                                                                       'trợ ngay lập '
                                                                                                       'tức hoặc có '
                                                                                                       'bất kỳ câu '
                                                                                                       'hỏi nào, '
                                                                                                       'xin vui lòng '
                                                                                                       'liên hệ với '
                                                                                                       'đội hỗ trợ '
                                                                                                       'của chúng '
                                                                                                       'tôi, '
                                                                                                       'và họ sẽ hỗ '
                                                                                                       'trợ bạn giải '
                                                                                                       'quyết vấn đề. '
                                                                                                       'Cảm ơn bạn đã '
                                                                                                       'kiên nhẫn.')

    @property
    def status_code(self):
        return self.value[0]

    @property
    def name(self):
        return self.value[1]

    @property
    def message(self):
        return self.value[2]
