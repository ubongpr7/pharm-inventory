
document.addEventListener('htmx:afterOnLoad', function(evt) {
  const contentDiv = evt.detail.target;
  console.log('target: ', contentDiv)
  const newTitle = contentDiv.querySelector('[data-title]')?.getAttribute('data-title');
  if (newTitle){
    document.getElementById('page-title').innerText = newTitle;

  }
});


document.addEventListener('htmx:configRequest', function(evt) {
  document.querySelector('.loader').style.display = 'block';
});

document.addEventListener('htmx:afterOnLoad', function(evt) {
  document.querySelector('.loader').style.display = 'none';
});

document.addEventListener('htmx:afterSwap', function(evt) {
  document.querySelector('.loader').style.display = 'none';
});
; (function () {
    const modal = new bootstrap.Modal(document.getElementById("modal"))

    htmx.on("htmx:afterSwap", (e) => {
      // Response targeting #dialog => show the modal
      if (e.detail.target.id == "dialog") {
        modal.show()
      }
    })

    
    htmx.on("htmx:beforeSwap", (e) => {
      // Empty response targeting #dialog => hide the modal
      if (e.detail.target.id == "dialog" && !e.detail.xhr.response) {
        modal.hide()
        e.detail.shouldSwap = false
      }
    })

    // Remove dialog content after hiding
    htmx.on("hidden.bs.modal", () => { 
        
      document.getElementById("dialog").innerHTML = ""
      // location.reload()
      
    })
    
  })()

  ; (function () {
    const toastElement = document.getElementById("toast")
    const toastBody = document.getElementById("toast-body")
    const toast = new bootstrap.Toast(toastElement, { delay: 2000 })

    htmx.on("showMessage", (e) => {
      toastBody.innerText = e.detail.value
      toast.show()
    })
  })()
document.querySelectorAll('a[data-target-div]').forEach(anchor=>{
    anchor.addEventListener('click',function(e){
      e.preventDefault();
      const targetId=this.getAttribute('data-target-div');
      const targetElement= document.getElementById(targetId)
      htmx.on('htmx:afterSwap', (event)=>{
        if (event.detail.target.id === targetId){
          targetElement.scrollIntoView({behavior:'smooth'})
        }
      })
    })
  })
  
  function closeContent(button){
  
  const contentDiv =document.getElementById(button.querySelector("[data-target]").getAttribute('data-target'))
  contentDiv.innerHTML=''            
  
}

function showLoader() {
  document.querySelector('.loader').style.display = 'block';
}

function hideLoader() {
  document.querySelector('.loader').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
  hideLoader();
})
showLoader()