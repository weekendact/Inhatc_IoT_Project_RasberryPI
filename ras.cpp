#include <opencv2/opencv.hpp>
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cstring>
#include <vector>

#define SERVER_IP "192.168.101.102"  // 노트북 IP
#define SERVER_PORT 9999             // 포트 번호

int main() {
    // 카메라 열기
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "카메라를 열 수 없습니다." << std::endl;
        return -1;
    }

    // UDP 소켓 설정
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "소켓 생성 실패" << std::endl;
        return -1;
    }

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &serverAddr.sin_addr);

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
                          (struct sockaddr*)&serverAddr, sizeof(serverAddr));
        if (sent < 0) {
            std::cerr << "데이터 전송 실패" << std::endl;
        } else {
            std::cout << "프레임 전송 완료 (" << buffer.size() << " bytes)" << std::endl;
        }

        // 0.5초 대기
        usleep(500000);
    }

    close(sock);
    return 0;
}
