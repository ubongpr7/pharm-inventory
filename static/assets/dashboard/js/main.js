const operateNavigations = (type, target, variables) => {

  let componentId = type === "dropdown" ? variables.target : variables.targetId;

  const targetId = type === "dropdown" ? target.querySelector(`[${componentId}]`).getAttribute(componentId) : target.getAttribute(componentId)

  const activeMenu = document.querySelector(`#${targetId}`)

  const nonTargeted = variables.components.map(drop => {
    const nonActiveId = drop.querySelector(`[${componentId}]`).getAttribute(componentId)
    const nonActive = document.querySelector(`#${nonActiveId}`)

    return nonActive
  })

  const filterExceptActive = nonTargeted.filter(target => target !== activeMenu)

  filterExceptActive.forEach(drop => drop.classList.remove(variables.active))

  if (activeMenu) activeMenu.classList.toggle(variables.active)

}

// Closing components
const closeComponents = (type, event, variables) => {

  const target = type === "dropdown" ? event.target.closest(`.${variables.menu}`) || event.target.closest(`[${variables.target}]`) : event.target.closest(`.${variables.menu}`) || event.target.closest(`.${variables.target}`)

  if (target) return

  variables.components.forEach(comp => {
    const menu = comp.querySelector(`.${variables.menu}`)
    if (menu.classList.contains(variables.active)) menu.classList.remove(variables.active)
  })

}




const dropdown = () => {
    const _variables = {
      main: "e-dropdown",
      menu: "e-dropdown__menu",
      target: "data-dropdown-target",
      active: "e-active",
    }
  
    const dropDown = [...document.querySelectorAll(`.${_variables.main}`)]
  
    document.addEventListener("click", (e) => {
  
      const target = e.target.closest(`.${_variables.main}`)
  
      const targetedMenu = e.target.closest(`.${_variables.menu}`)
  
      if (!target || targetedMenu) return
  
      const targetId = target.querySelector(`[${_variables.target}]`).getAttribute(_variables.target)
  
      const activeMenu = document.querySelector(`#${targetId}`)
  
      const nonTargeted = dropDown.map(drop => {
        const nonActiveId = drop.querySelector(`[${_variables.target}]`).getAttribute(_variables.target)
        const nonActive = document.querySelector(`#${nonActiveId}`)
  
        return nonActive
      })
  
      const filterExceptActive = nonTargeted.filter(target => target !== activeMenu)
      if (filterExceptActive){

        filterExceptActive.forEach(drop =>{
          if (drop){
            drop.classList.remove(_variables.active)
          }
        })
      }
  
      if (activeMenu) activeMenu.classList.toggle(_variables.active)
  
    })
  
  }
  
  dropdown()



