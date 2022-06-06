/*
 * main.c
 *
 *  Created on: 06.06.2022
 *      Author: swt
 */
#include "smartbit.c"
#include <unistd.h>

int main(){
	const char* path = "./protocol.json";
	const char* file_content = get_file_content(path);

	float prox = get_prox(file_content);

	while (1){
		prox = get_prox(file_content);
		if(prox == 0.0){
			for(int i =0 ; i < 5; i++){
				vibrate(file_content, 1000);
				toggle_button(file_content);
				write_text(file_content, "Alarm");
			}
		}
		sleep(1);
		write_text(file_content, "output");
	}

	free(file_content);
}
