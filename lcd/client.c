
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <syslog.h>
#include "wiringpi.h"
#include "lcd.h"

/* macros */
#define MAX 80
#define PORT 9000
#define SA struct sockaddr
#define FILE_PATH "/root/home/socketdata"

/*static int lcd_addr[] = {0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88,0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F,
                       0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8 ,0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF,
	               0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0X97, 0x98, 0x99, 0x9A, 0x9B, 0x9C ,0x9D, 0x9E, 0x9F,
	               0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xDB, 0xDC ,0xDD, 0xDE, 0xDF};

*/
/* function definition */


/* main function */
int main(int argc, char *argv [])
{
        /* initialization */
        int sockfd, connfd;
	char *ip_addr = NULL;
	if (argc>1)
	{
		ip_addr = argv[1];
	}     
  	else
	{
		ip_addr ="10.0.0.212";
	} 	
        struct sockaddr_in server_addr;
        //open connection for sys logging, ident is NULL to use this Program for the user level messages
        openlog(NULL, LOG_CONS | LOG_PID | LOG_PERROR, LOG_USER);
        
        //create socket
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd == -1) 
        {
                syslog(LOG_ERR, "fail to create socket");
                exit(0);
        }
        else
                syslog(LOG_DEBUG,"Socket successfully created");
        bzero(&server_addr, sizeof(server_addr));
	
	
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = inet_addr(ip_addr);
        server_addr.sin_port = htons(PORT);

        connfd = connect(sockfd, (SA*)&server_addr, sizeof(server_addr));

        if (connfd <0) 
        {
                syslog(LOG_ERR, "fail to connect with the server");
                exit(0);
        }
        else
                syslog(LOG_DEBUG, "connected to the server");
        
        //open or create file
        int fd =open(FILE_PATH, (O_RDWR|O_CREAT|O_APPEND),0766);
	if (fd == -1)
	{
		syslog(LOG_ERR,"The file could not be created/found");
		exit(4);
        }
        
        
        //close the file descriptor and the socket
        close(fd);
        close(sockfd);
        return 0;
}

