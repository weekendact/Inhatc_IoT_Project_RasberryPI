#include <opencv2/opencv.hpp>
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cstring>

#define PORT 9999
#define BROADCAST_IP "192.168.1.255"

int main() {
    // OpenCV로 카메라 열기
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "카메라를 열 수 없습니다." << std::endl;
        return -1;
    }

    // 소켓 설정
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "소켓 생성 실패" << std::endl;
        return -1;
    }

    int broadcastEnable = 1;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &broadcastEnable, sizeof(broadcastEnable));

    sockaddr_in broadcastAddr{};
    broadcastAddr.sin_family = AF_INET;
    broadcastAddr.sin_port = htons(PORT);
    inet_pton(AF_INET, BROADCAST_IP, &broadcastAddr.sin_addr);

    while (true) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "프레임 읽기 실패" << std::endl;
            break;
        }

        // 프레임을 JPEG로 압축
        std::vector<uchar> buffer;
        cv::imencode(".jpg", frame, buffer);

        // 데이터 전송
        int sent = sendto(sock, buffer.data(), buffer.size(), 0,
                          (struct sockaddr*)&broadcastAddr, sizeof(broadcastAddr));
        if (sent < 0) {
            std::cerr << "데이터 전송 실패" << std::endl;
        }

        std::cout << "프레임 전송 완료 (" << buffer.size() << " bytes)" << std::endl;

        // 0.5초 대기
        usleep(500000);
    }

    close(sock);
    return 0;
}
