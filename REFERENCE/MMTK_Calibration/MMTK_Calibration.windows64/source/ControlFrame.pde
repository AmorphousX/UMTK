// the ControlFrame class extends PApplet, so we 
// are creating a new processing applet inside a
// new frame with a controlP5 object loaded
public class ControlFrame extends PApplet {

  int w, h;

  float mmtkVel = 50.0;
  int bgColor = 200;

  public void settings() {
    size(400, 150);
    
  }

  public void setup() {
    surface.setLocation(100, 100);
    surface.setResizable(true);
    surface.setVisible(true);
    frameRate(25);
    cp5 = new ControlP5(this);


    int x = 0;
    int y = 0;
    
    fill(0, 0, 0);
    
    cp5.addTextlabel("label")
      .setText("MMTK Calibration")
      .setPosition(x=15, y=5)
      .setColorValue(color(0, 0, 0))
      .setFont(createFont("Arial", 22));
    
    
    cp5.addButton("5kg calibration")
      .setValue(1)
      .setColorBackground(color(0, 102, 204))
      .setFont(createFont("Arial Black", 10))
      .setPosition(x=15, y=50)
      .setSize(250,25);
      
   cp5.addButton("Tare")
      .setValue(1)
      .setFont(createFont("Arial Black", 10))
      .setPosition(x=15, y=85)
      .setSize(250,25);
 
 

    textFont(createFont("Arial", 16, true));

  }



  void controlEvent(ControlEvent theEvent) {
    print(theEvent);
    if (theEvent.isAssignableFrom(Textfield.class) || theEvent.isAssignableFrom(Toggle.class) || theEvent.isAssignableFrom(Button.class)) {
      String parameter = theEvent.getName();
      String value = "";
      if (theEvent.isAssignableFrom(Textfield.class))
        value = theEvent.getStringValue();
      else if (theEvent.isAssignableFrom(Toggle.class) || theEvent.isAssignableFrom(Button.class))
        value = theEvent.getValue()+"";

      print("set "+parameter+" "+value+";\n");
      
      if (parameter == "input speed") {
        mmtkVel = float(value);
        serialPort.write("V" + mmtkVel + "\n");
      }
      
      
      // Send Serial Commands to MMTK
      if (!mockupSerial) {
        if (parameter == "Start") {
          serialPort.write("Begin\n");
        } else if (parameter == "Tare") {
          serialPort.write("Tare\n");
        } else if (parameter == "Stop") {
          serialPort.write("Stop\n");
        } else if (parameter == "5kg calibration"){
          serialPort.write("Calibration\n");
        }
      }
      
    }
  }

  public void draw() {
    background(bgColor);
  }

  private ControlFrame() {
  }

  public ControlFrame(PApplet theParent, int theWidth, int theHeight, String _name) {
    parent = theParent;
    w = theWidth;
    h = theHeight;
    PApplet.runSketch(new String[]{this.getClass().getName()}, this);
  }


  public ControlP5 control() {
    return cp5;
  }


  ControlP5 cp5;

  PApplet parent;
}
