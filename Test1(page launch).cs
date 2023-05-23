using NUnit.Framework;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;

namespace Test
{
    class Program
    {
        [Test]
        static void Main(string[] args)
        {
            Console.Write("start");
            IWebDriver driver = new ChromeDriver("C:/Users/Aslambek/Desktop");
            driver.Navigate().GoToUrl("http://localhost:4200/towns");
            IJavaScriptExecutor js = (IJavaScriptExecutor)driver;
            var ResponseTime = Convert.ToInt32(js.ExecuteScript("return window.performance.timing.domContentLoadedEventEnd-window.performance.timing.navigationStart;"));
            Console.WriteLine(string.Format("Page {0} loading time is {1} ms", driver.Title, ResponseTime));
            Console.Write("end");
            driver.Close();
        }
    }
}


