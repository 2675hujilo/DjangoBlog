// 获取保存密码的缓存数据
function check() {
  let checkbox = document.getElementById("remember-pw");
  let username = document.getElementById("username").value;
  let password = document.getElementById("password").value;

  // 如果勾选了“记住密码”，则保存密码
  if (checkbox.checked) {
    localStorage.setItem("username", username);
    localStorage.setItem("password", password);
  }
}

// 判断是否存在保存的密码，并自动填充表单
function init() {
  let username = localStorage.getItem("username");
  let password = localStorage.getItem("password");

  if (username !== null && password !== null) {
    document.getElementById("username").value = username;
    document.getElementById("password").value = password;
  }
}

// 在页面加载完成时运行init函数
window.onload = () => {
  init();
  
  // 当表单提交时，先检查勾选情况再执行check函数
   document.querySelector('form').addEventListener('submit', (event) => {
     check();
   });
}