console.log('htmx functions are running')
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


// tabular display functions


// Create functions
// document.addEventListener("htmx:afterRequest",(event)=>{
//     if (event.detail.target.id ==="model-body"){
//         var modal =new bootstrap.Modal(document.getElementById('sub-form'));
//         modal.show();
//         console.log('shown')

//     }
// })
// document.addEventListener('htmx:afterRequest',(e)=>{
//     if (e.detail.verb ==="POST"){
        
//         let newCategory=event.detail.xhr.response;
//         let select=document.getElementById('id_category');
//         let option=document.createElement('option');
//         option.value=newCategory.id
//         option.text=newCategory.name
//         select.add(option);
//         select.value=newCategory.id
//         let modal =bootstrap.Modal.getInstance(document.getElementById('sub-form'))
//         modal.hide();
//     }
// })
