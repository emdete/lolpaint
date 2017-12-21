#include <Charliplexing.h>

static int BAUD = 19200;
static byte WIDTH = 14;
static byte HEIGHT = 9;
static int bufpos = -1;
static byte buf[500];

void setup() {
	LedSign::Init();
	Serial.begin(BAUD);
  for (int i=0;i<HEIGHT;i++) {
    for (int j=0;j<WIDTH;j++) {
      LedSign::Set(j, i, 0);
    }
  }
  for (int i=0;i<HEIGHT;i++) {
    for (int j=0;j<WIDTH;j++) {
      LedSign::Set(j, i, 0);
    }
  }
}

void loop () {
	while (Serial.available() >= 1) {
		unsigned char received = Serial.read();
		switch (received) {
		case 255:
		break;
		case 254:
			bufpos = -1;
		break;
		case 253:
			bufpos = 0;
		break;
		default:
			if (bufpos >= 0) {
				buf[bufpos++] = received;
				bufpos %= sizeof(buf);
			}
			int val = received % 2;
			received /= 2;
			byte x = received % WIDTH;
			received /= WIDTH;
			byte y = received % HEIGHT;
			received /= HEIGHT;
			LedSign::Set(x,y,val);
			break;
		}
	}
}

