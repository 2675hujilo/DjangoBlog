function check() {
  let checkbox = document.getElementById("remember-pw");
  let username = document.getElementById("username").value;
  let password = document.getElementById("password").value;

  // 如果勾选了“记住密码”，则保存密码和状态
  if (checkbox.checked) {
    localStorage.setItem("username", username);
    localStorage.setItem("password", password);
    localStorage.setItem("remembered", checkbox.checked);
  } else {
    localStorage.removeItem("remembered");

    const rememberedPassword = localStorage.getItem("password"); 
    if(rememberedPassword != null) {  
      localStorage.removeItem("password");
    }
  }
}

// 判断是否存在保存的密码，并自动填充表单，同时也填充记住密码的checkbox框
function init() {
  let username = localStorage.getItem("username");
  let password = localStorage.getItem("password");
  let remembered = localStorage.getItem("remembered");

  if (username !== null && password !== null) {
    document.getElementById("username").value = username;
    
     // 检查是否勾选记住密码。如果没有勾选，删除本地密码
    if (remembered === "true") {
      document.getElementById("password").value = password;
      document.getElementById("remember-pw").checked = true;
    } else {
      document.getElementById("password").value = '';
      localStorage.removeItem('password');
      document.getElementById("remember-pw").checked = false;
      localStorage.removeItem('remembered');
    }
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
