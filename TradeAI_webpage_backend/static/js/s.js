/*var submitButton = document.getElementById('submit');
let buttonClicked = false;
submitButton.addEventListener('click', function handleClick() {
 console.log('Submit button is clicked');
 if (buttonClicked) {
  console.log('Submit button has already clicked');
 }
 buttonClicked = true;
});
*/

window.addEventListener('mouseover', function() {
    if(540 < this.window.innerWidth && this.window.innerWidth < 1260)
    {
        this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
        this.document.getElementById('maccount-center').style.boxShadow = "none";
        this.document.getElementById('account-center').style.visibility = 'hidden';
    }
    else {
        if(this.window.innerWidth < 1620 && this.window.innerWidth >= 1560) {
            console.log(this.window.innerWidth);
            this.document.getElementById('main').style.width = "calc(100vh - 30vh)"
            this.document.getElementById('maccount-center').style.width = "480px";
            this.document.getElementById('addCashButton').style.width = "100px";
        } else if(this.window.innerWidth < 1560 && this.window.innerWidth > 1220)
        {
            this.document.getElementById('main').style.width = "calc(100vh - 40vh)";
            /*this.document.getElementById('account-center').style.display = 'none';*/
            this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
            this.document.getElementById('maccount-center').style.boxShadow = "none";
            this.document.getElementById('account-center').style.visibility = 'hidden';
        }
    }

    /*if(540 > this.window.innerWidth) {
        this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
        this.document.getElementById('maccount-center').style.boxShadow = "none";
        this.document.getElementById('account-center').style.visibility = 'hidden';

        this.document.getElementById('main').style.left = '100px';
        this.document.getElementById('main').style.width = "calc(100vh - 75vh)";
    } else {*/
        if(this.window.innerWidth < 815 && this.window.innerWidth >= 680) {
            this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
            this.document.getElementById('maccount-center').style.boxShadow = "none";
            this.document.getElementById('account-center').style.visibility = 'hidden';
            this.document.getElementById('main').style.left = '100px';
            this.document.getElementById('main').style.width = "calc(100vh - 60vh)";
        } else {
            if(this.window.innerWidth < 680) {
                /* TODO: Add support for screen width/height of phones */
                this.document.getElementById('main').style.left = '15px';
                this.document.getElementById('main').style.width = "475px";
                this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
                this.document.getElementById('maccount-center').style.boxShadow = "none";
                this.document.getElementById('account-center').style.visibility = 'hidden';
            }
        }
    

    if(this.window.innerWidth >= 1660) {
        this.document.getElementById('account-center').style.visibility = 'visible';
        this.document.getElementById('maccount-center').style.backgroundColor = 'white';
        this.document.getElementById('maccount-center').style.width = "540px";
        this.document.getElementById('addCashButton').style.width = "156.5px";
        this.document.getElementById('logoutButton').style.width = '156.5px';
        this.document.getElementById('takeoutCashButton').style.width = '156.5px';

        //this.document.getElementById('main').style.left = '35%';
        //this.document.getElementById('main').style.width = "calc(100vh - 20vh)";
        this.document.getElementById('maccount-center').style.boxShadow = '4px 4px 12px green';
    }
});

let all_ids_to_toggle = ['orderHistory', 'investmentStats', 'settings', 'committedData', 'stockPreview', 'api', 'account-center', 'stockPreviewBelowAccount'];
let all_btp = ['btp1', 'btp2', 'btp3', 'btp4', 'btp5', 'btp6'];
let all_values = {
    'btp1': 'Order History',
    'btp2': 'Investment Stats',
    'btp3': 'Settings',
    'btp4': 'Committed Data',
    'btp5': 'API Docs',
    'btp6': 'Account'
}

window.onload = function() {
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    document.getElementById('stockPreview').style.display = 'block';
}

function toggleRecents() {
    let x = document.getElementById('recent');

    if(x.style.display == 'none') {
        x.style.display = 'block';
        hide_recents = false;
    } else { x.style.display = 'none'; }
}

function check_all_are_hidden() {
    let number = 0;
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(document.getElementById(all_ids_to_toggle[i]).style.display == 'none') {number++;}
    }

    if(number == all_ids_to_toggle.length) { document.getElementById('stockPreview').style.display = 'block'; }
    else {
        if(document.getElementById('stockPreview').style.display != 'none') { document.getElementById('stockPreview').style.display = 'none'; }
    }
}

function change_all_back() {
    for(let i = 0; i < all_btp.length; i++) {
        document.getElementById(all_btp[i]).innerText = all_values[all_btp[i]];
        document.getElementById(all_btp[i]).style.border = '1px solid black';
    }
}

function toggleOrderHistory() {
    let x = document.getElementById('orderHistory');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'orderHistory') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp1').innerText = 'Back';
        document.getElementById('btp1').style.border = '1px solid greenyellow';
    } else { x.style.display = 'none'; document.getElementById('btp1').innerText = 'Order History'; document.getElementById('btp1').style.border = '1px solid black';}

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

function toggleSettings() {
    let x = document.getElementById('settings');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'settings') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp3').innerText = 'Back';
        document.getElementById('btp3').style.border = '1px solid greenyellow';
    } else { x.style.display = 'none'; document.getElementById('btp3').innerText = 'Settings'; document.getElementById('btp3').style.border = '1px solid black';}

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

function toggleCommittedData() {
    let x = document.getElementById('committedData');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'committedData') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp4').innerText = 'Back';
        document.getElementById('btp4').style.border = '1px solid greenyellow';
    } else { x.style.display = 'none'; document.getElementById('btp4').innerText = 'Committed Data'; document.getElementById('btp4').style.border = '1px solid black'; }

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

function toggleInvestmentStats() {
    let x = document.getElementById('investmentStats');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'investmentStats') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp2').innerText = 'Back';
        document.getElementById('btp2').style.border = '1px solid greenyellow';
    } else { x.style.display = 'none'; document.getElementById('btp2').innerText = 'Investment Stats'; document.getElementById('btp2').style.border = '1px solid black'; }

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

function toggleApiDocs() {
    let x = document.getElementById('api');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'api') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp5').innerText = 'Back';
        document.getElementById('btp5').style.border = '1px solid greenyellow';
    } else { x.style.display = 'none'; document.getElementById('btp5').innerText = 'API Docs'; document.getElementById('btp5').style.border = '1px solid black'; }

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

function toggleAccount() {
    let x = document.getElementById('account-center');
    
    for(let i = 0; i < all_ids_to_toggle.length; i++) {
        if(all_ids_to_toggle[i] == 'account-center') continue;
        document.getElementById(all_ids_to_toggle[i]).style.display = 'none';
    }

    if(x.style.display == 'none') {
        change_all_back();
        x.style.display = 'block';
        document.getElementById('btp6').innerText = 'Back';
        document.getElementById('btp6').style.border = '1px solid greenyellow';
        document.getElementById('stockPreviewBelowAccount').style.display = 'block';
    } else { document.getElementById('stockPreviewBelowAccount').style.display = 'none'; x.style.display = 'none'; document.getElementById('btp6').innerText = 'Account'; document.getElementById('btp6').style.border = '1px solid black'; }

    if(x.style.display == 'none') { check_all_are_hidden(); }
}

window.addEventListener('resize', function() {
    if(this.innerWidth >= 1360) {
        this.document.getElementById('account-center').style.visibility = 'visible';
        this.document.getElementById('maccount-center').style.backgroundColor = 'white';
        this.document.getElementById('maccount-center').style.width = "540px";
        this.document.getElementById('addCashButton').style.width = "156.5px";
        this.document.getElementById('logoutButton').style.width = '156.5px';
        this.document.getElementById('takeoutCashButton').style.width = '156.5px';
        this.document.getElementById('main').style.left = '35%';
        this.document.getElementById('main').style.width = "calc(100vh - 20vh)";
        this.document.getElementById('maccount-center').style.boxShadow = '4px 4px 12px green';
    }
    /* TODO: Add support for screen width/height of phones */
    if(this.window.innerWidth >= 1620)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 20vh)";
        return;
    } 
    if(this.window.innerWidth < 1620 && this.window.innerWidth >= 1560) {
        this.document.getElementById('main').style.width = "calc(100vh - 30vh)"
        this.document.getElementById('maccount-center').style.width = "480px";
        this.document.getElementById('addCashButton').style.width = "100px";
    }
    else if(this.window.innerWidth < 1560 && this.window.innerWidth >= 1220)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 40vh)";
        /*this.document.getElementById('account-center').style.display = 'none';*/
        this.document.getElementById('maccount-center').style.backgroundColor = 'transparent';
        this.document.getElementById('maccount-center').style.boxShadow = "none";
        this.document.getElementById('account-center').style.visibility = 'hidden';
    }
    else if(this.window.innerWidth < 1220 && this.window.innerWidth >= 1020)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 50vh)";
    }
    else if(this.window.innerWidth < 1020 && this.window.innerWidth >= 920)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 55vh)";
    }
    else if(this.window.innerWidth < 920 && this.window.innerWidth >= 815)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 60vh)";
    }
    else {
        if(this.window.innerWidth < 815) {
            if(this.window.innerWidth > 680) {
                this.document.getElementById('main').style.left = '100px';
                this.document.getElementById('main').style.width = "calc(100vh - 60vh)";
            } else {
                this.document.getElementById('main').style.left = '15px';
                this.document.getElementById('main').style.width = "475px";
            }        
        } else {
            console.log('here');
            document.getElementById('main').style.width = "calc(100vh - 20vh)";
        }
    }
});

window.addEventListener('reload', function() {
    console.log(this.window.innerWidth);
    if(this.window.innerWidth < 1620 && this.window.innerWidth > 1420) {
        this.document.getElementById('main').style.width = "calc(100vh - 30vh)"
    }
    else if(this.window.innerWidth < 1420 && this.window.innerWidth > 1220)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 40vh)";
    }
    else if(this.window.innerWidth < 1220 && this.window.innerWidth > 1020)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 50vh)";
    }
    else if(this.window.innerWidth < 1020 && this.window.innerWidth > 820)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 55vh)";
    }
    else if(this.window.innerWidth < 820 && this.window.innerWidth > 620)
    {
        this.document.getElementById('main').style.width = "calc(100vh - 60vh)";
    }
    else {
        if(this.window.innerWidth < 620) {
            this.document.getElementById('main').style.width = "calc(100vh - 75vh)";
        } else {
            document.getElementById('main').style.width = "calc(100vh - 20vh)";
        }
    }
});