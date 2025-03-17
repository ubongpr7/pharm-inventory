
function getItems(url="{% url 'common:item_list' app_label user.company.encrypted_id model_label  %}"){
    
    htmx.ajax('GET', url,{target:'#main-container-div-content'})
    console.log('gotten')    
}

function updateItems(){
    console.log('updateItems')
    const _variables={
    model_name:"{{ model_label }}",
    app_name:"{{ app_label }}"

    }
    const modelDiv= document.getElementById("main-container-div-content")

    if (document.getElementById(`delete-form`)){
      console.log('delete-form')
      document.getElementById(`delete-form`).addEventListener('htmx:afterOnLoad',()=>{
        
        console.log('deleted')
        getItems()

    })
    }

    if (document.getElementById(`main-container-div-form`)){
        const modelForm= document.getElementById(`main-container-div-form`)
        console.log(modelDiv)
    modelForm.addEventListener('htmx:afterOnLoad',()=>{
        console.log('Item added')

        getItems()
        
    })
    }

}

updateItems();
function saveOrderingPreference(item,order) {
  localStorage.setItem(`${item}_odering`, order);
}
function getOrderingPreference(item) {
  return localStorage.getItem(`${item}_odering`) || null ;
}

function companyID(){
  
  if ('{{user.company }}'){
    return "{{user.company.encrypted_id}}"
    
  }
  else if ('{{user.profile }}'){
    return "{{user.profile.encrypted_id}}"
  }
    
}

function updateQueryParam(button,param, value) {
  const app_label=button.getAttribute('data-app')
  const model_label=button.getAttribute('data-model')
  if (param === 'order_by'){
    saveOrderingPreference(model_label,value)

    const listUrl= `/list/${app_label}/${companyID()}/${model_label}/?${param}=${value}`
    getItems(listUrl)
  }
  else if (param === 'filter'){
    const listUrl= `/list/${app_label}/${companyID()}/${model_label}/?order_by=${getOrderingPreference(model_label)}&filter_field=${value}&${param}=${1}`
    getItems(listUrl)

    }

  }