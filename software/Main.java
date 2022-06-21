
public class Main {

	
	public static void main(String[] args) {
		Phone p = new Phone("/home/swt/eclipse-workspace/alarm_java/src/protocol.json");
		float prox = p.get_prox();
		while (true) {
			prox = p.get_prox();
			if(prox == 0.0) {
				p.writeText("Alarm");
				for(int i = 0; i <5 ; i ++) {
					p.vibrate(1000);
					p.buttonToggle();
					try {
						Thread.sleep(200);
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			}
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
}
