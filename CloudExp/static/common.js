/* Write JS here */
"use strict";
function sideMenu() {
  var e = document.querySelectorAll(".hamburger"),
    n = document.querySelector(".mobile-nav");
  console.log(e),
    e.forEach(function (e) {
      e.addEventListener("click", function (e) {
        n.classList.toggle("grid"), n.classList.toggle("none");
      });
    });
}
function toggleAdminMenu() {
  const languages = document.querySelector('.admin-panel-main__languages');

  languages.addEventListener('click', (event) => {
      const target = event.target;
      console.log(target);
      if(target.classList.contains('admin-panel-main__button')) {
          target.nextElementSibling.classList.toggle('hidden');
          target.nextElementSibling.classList.toggle('show');
      }
  })
}

function insertTag() {
  const textarea = document.querySelector('#admin-panel-main__text-chapter');
  let startPos = textarea.selectionStart;
  let endPos = textarea.selectionEnd;
  
  const container = document.querySelector('#btns-cont');

  textarea.onclick = () => {
      startPos = textarea.selectionStart;
      endPos = textarea.selectionEnd;
      console.log(startPos, endPos)
  }

  container.addEventListener('click', (event) => {
      const target = event.target;
      startPos = textarea.selectionStart;
      endPos = textarea.selectionEnd;
      console.log(startPos, endPos)
      function insertTag(tag) {
          textarea.value = textarea.value.substring(0, startPos) + tag + textarea.value.substring(endPos, textarea.value.length);
      }
      
      if(target.classList.contains('admin-panel-main__h1')) {
          insertTag("<h1 class='chapter-main-content__title'></h1>");
      }
      
      if(target.classList.contains('admin-panel-main__h2')) {
          insertTag('<h2></h2>');
      } 
      
      if(target.classList.contains('admin-panel-main__h3')) {
          insertTag('<h3></h3>');
      }
      
      if(target.classList.contains('admin-panel-main__ul')) {
          insertTag('<ul><li></li></ul>');
      }
      
      if(target.classList.contains('admin-panel-main__ol')) {
          insertTag('<ol><li></li></ol>');
      }
      
      if(target.classList.contains('admin-panel-main__p')) {
          insertTag("<p class='chapter-main-content__text'></p>");
      }
      
      if(target.classList.contains('admin-panel-main__img')) {
          insertTag('<img src="" alt=""></img>');
      }
      
      if(target.classList.contains('admin-panel-main__highlightjs')) {
          insertTag('<pre><code class="hljs"></code><pre>');
      }
  });
}

function toggleSolution() {
    const btns = document.querySelectorAll('.task__solution-btn');
    
    btns.forEach((btn) => {
        btn.onclick = function() {
            let element = this.parentElement.querySelector('.task__solution-code');
            element.classList.toggle('hidden');
            element.classList.toggle('show');
            if (btn.textContent == "Показать решение") {
                btn.textContent = "Скрыть решение";
            } else {
                btn.textContent = "Показать решение"
            }
            console.log(element);
        };
    });
}


function toggleHint() {
    const btns = document.querySelectorAll('.task-solution-hint__btn');
    
    btns.forEach((btn) => {
        btn.onclick = function() {
            let element = this.parentElement.querySelector('.task-solution-hint__popup');
            element.classList.toggle('hidden');``
            element.classList.toggle('show');
            console.log(element);
        };
    });
}

toggleSolution();
toggleHint();
hljs.initHighlightingOnLoad();
sideMenu();
toggleAdminMenu(); 
insertTag();
