using NUnit.Framework;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Interactions;
using OpenQA.Selenium.Support.UI;
using System.Diagnostics;

namespace Test
{
    class Program
    {
        [Test]
        static void Main(string[] args)
        {
            DateTime date = DateTime.Now;
            Console.Write("start");
            IWebDriver driver = new ChromeDriver("C:/Users/Aslambek/Desktop");
            driver.Navigate().GoToUrl("http://localhost:4200/towns");
            driver.Manage().Window.Maximize();
            IWebElement download = (new WebDriverWait(driver, new TimeSpan(0, 0, 30))).Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementIsVisible(By.XPath("/html/body/town-finder/div/app-city-list/div/div/a[1]/div[2]")));
            download.Click();
            IWebElement red = (new WebDriverWait(driver, new TimeSpan(0, 0, 30))).Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementToBeClickable(By.XPath("//*[name()='g']/*[name()='path'][2]")));
            IWebElement create = driver.FindElement(By.XPath("/html/body/town-finder/div/app-town/div/div[1]/app-map/div/div[2]/div[1]/div[3]/a[1]"));
            create.Click();
            Thread.Sleep(200);
            IWebElement map = (new WebDriverWait(driver, new TimeSpan(0, 0, 30))).Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementIsVisible(By.XPath("/html/body/town-finder/div/app-town/div/div[1]/app-map/div")));
            Actions act = new Actions(driver);
            act.MoveToElement(map).Click();
            act.MoveToElement(map, 40, 5).Click();
            act.MoveToElement(map, 10, 15).Click();
            act.MoveToElement(map).Click();
            act.Build().Perform();
            IWebElement town = (new WebDriverWait(driver, new TimeSpan(0, 0, 30))).Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementToBeClickable(By.XPath("//*[name()='g']/*[name()='path'][2]")));
            Thread.Sleep(5000);
            town.Click();
            Thread.Sleep(200);
            IWebElement get = driver.FindElement(By.XPath("/html/body/town-finder/div/app-town/div/div[1]/app-map/div/div[1]/div[6]/div/div[1]/div/div/button"));
            Stopwatch stopwatch = new Stopwatch();
            stopwatch.Start();
            get.Click();
            IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
            var ResponseTime = Convert.ToInt32(js.ExecuteScript("return window.performance.timing.domContentLoadedEventEnd-window.performance.timing.navigationStart;"));
            Console.WriteLine(string.Format("Page {0} loading time is {1} ms", driver.Title, ResponseTime));
            IWebElement check = new WebDriverWait(driver, new TimeSpan(0, 0, 600)).Until(SeleniumExtras.WaitHelpers.ExpectedConditions.ElementToBeClickable(By.XPath("/html/body/town-finder/div/app-town/div/div[4]/button[3]")));
            check.Click();
            stopwatch.Stop();
            Console.WriteLine("The construction of the graph took: {0} s", stopwatch.ElapsedMilliseconds / 1000);
            Console.Write("end");
        }
    }
}
