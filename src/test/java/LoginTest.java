import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.testng.annotations.Test;

public class LoginTest {

@Test
public void openTrashApp() {

WebDriverManager.chromedriver().setup();

WebDriver driver = new ChromeDriver();

driver.get("http://localhost:5000");

System.out.println("TrashApp opened successfully");

driver.quit();
}
}