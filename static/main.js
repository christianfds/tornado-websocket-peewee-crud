const MDCRipple = mdc.ripple.MDCRipple
const MDCTopAppBar = mdc.topAppBar.MDCTopAppBar
const MDCTextField = mdc.textField.MDCTextField
const MDCSnackBar = mdc.snackbar.MDCSnackbar
const MDCMenuSurface = mdc.menuSurface.MDCMenuSurface

let products = [];
let snack_bar;
let my_menu;

$(document).ready(function () {
    
    updater.start();

    getProdutos(() => build_product_grid())
    // mdc.autoInit()
    
    setRipple();
    $('.mdc-button, .mdc-icon-button, .mdc-card__primary-action').each((_i, e) => {
        new MDCRipple(e);
    })
    
    new MDCTopAppBar(document.querySelector('.mdc-top-app-bar'));
    my_menu = new MDCMenuSurface(document.querySelector('.mdc-menu-surface'));
    snack_bar = new MDCSnackBar(document.querySelector('.mdc-snackbar'))

    $('.menu-button').click(() => {
        $.ajax({
            type: "GET",
            url: "/produto/cart",
            dataType: "json",
            success: function (response) {
                $('#shoppingList').text('');
                response.forEach((e,i)=>{
                    console.log(e)
                    $('#shoppingList').append($(' \
                        <li class="mdc-list-item" role="menuitem" > \
                            <span class="mdc-list-item__text"><b>'+e.nome+'</b> x '+e.quantidade+' - R$'+e.preco * e.quantidade+'</span> \
                        </li> \
                    '))
                })
                // shopping_list
                my_menu.open = true;
            }
        });
    })
});

function setTextField(){
    $('.mdc-text-field').each((_i, e) => {
        new MDCTextField(e);
    })
}

function setRipple(){
    $('.mdc-button, .mdc-icon-button, .mdc-card__primary-action, .mdc-line-ripple').each((_i, e) => {
        new MDCRipple(e);
        // console.log(e)
    })
}

function getProdutos(callback){
    $.ajax({
        type: "GET",
        url: "/produtos",
        // data: "data",
        dataType: "json",
        crossDomain: true,
        success: function (response) {
            products = response;
            callback();
        }
    });
}

function build_product(element){
    jq_element = $(' \
    <div class="mdc-layout-grid__cell mdc-layout-grid__cell--span-3"> \
        <div class="mdc-card item_shop"> \
            <div class="mdc-card__primary-action"> \
                <div class="mdc-card__media mdc-card__media--square" style="background-image: url('+ '/static/' + element.img_path +'); background-size: contain;"> \
                    <div class="mdc-card__media-content"><div class="price mdc-theme--primary-bg"><span class="mdc-theme--on-primary">'+element.preco+'</span></div></div> \
                </div> \
            </div> \
            <div class="mdc-card__actions"> \
                <div class="mdc-card__action-buttons"> \
                    <span>'+element.nome+'</span> \
                </div> \
                <div class="mdc-card__action-icons"> \
                    <button class="mdc-button card-buy"><span class="mdc-button__label"><span class="material-icons">add_shopping_cart</span></span></button> \
                </div> \
            </div> \
        </div> \
    </div> \
    ');

    jq_element.find('.mdc-card__actions button').click(function (e){
        e.preventDefault();

        $.ajax({
            type: "POST",
            url: "/produto/add",
            crossDomain: true,
            data: {
                "produtoid": element.id
            },
            dataType: "json",
            success: function () {
                snack_bar.labelEl_.innerText = 'Produto adicionado ao carrinho'
                snack_bar.open();
            }
        });
    });

    return jq_element;
}

function build_product_grid(){
    father = $('#product_grid .mdc-layout-grid__inner');
    // console.log(father);

    father.text('')

    products.forEach(element => {
        father.append($(build_product(element)));
    });

    setRipple();
}

let updater = {
    start : () => {
        let url = "ws://" + window.location.host + "/cart/updates"
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function (event) {
            result = JSON.parse(event.data)
            if(result.type == "PING"){
                console.log('Conectado');
            }
            else if(result.type == "UPDATE"){
                updater.updateCarrinho(result.quantity)
            }
            else{
                // updater.showMessage(event);
            }
        }
    },
    
    showMessage : message => {
        console.log(message)
    },

    updateCarrinho : ammount => {
        $('#n_produtos').text(ammount + '  ')
    }
}