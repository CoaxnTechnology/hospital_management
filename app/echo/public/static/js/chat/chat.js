'use_strict';

let tempDiscussionItem;
let tempDiscussionPopup;
let tempMsgIn;
let tempMsgOut;
let users;
let popups = [];
let discussions = [];
let sockets = {};
let eventSocket;
let socketProtocol = location.protocol === 'https:' ? 'wss' : 'ws'
const msgAlert = new Audio('/static/sounds/bip.mp3');
msgAlert.volume = 0.1;
const socketBaseUrl = socketProtocol + '://' + window.location.host + '/ws/discussion/';

function trouverDiscussion(opponentId) {
    return _.find(discussions, d => (d.owner.id == user && d.opponent.id == opponentId) || (d.owner.id == opponentId && d.opponent.id == user));
}

function initaliserEventSocket() {
    url = socketProtocol + '://' + window.location.host + '/ws/events/' + user + '/';
    eventSocket = new WebSocket(url);
    eventSocket.onmessage = (event) => traiterEvenement(event);
    eventSocket.onopen = () => {
        let msg = JSON.stringify({
            message: 'ping'
        });
        eventSocket.send(msg);
    };
}

function connecter(discussionId) {
    url = socketBaseUrl + discussionId + '/';
    websocket = new WebSocket(url);
    sockets[discussionId] = websocket;
    websocket.onmessage = (event) => traiterMessage(event);
    websocket.onopen = () => {
        console.log("Socket ouverte pour la discussion", discussionId);
    };
}

function traiterEvenement(event) {
    console.log('Received event', event);
    const data = JSON.parse(event.data);
    console.log('Received data', data);
    if (data.type === 'incoming_msg') {
        disc = _.find(discussions, {id: parseInt(data.discussion)});
        const id = parseInt(disc.owner.id == user ? disc.opponent.id : disc.owner.id);
        if (!sockets[disc.id]) {
            console.log('Socket non trouvée');
            ouvrirDiscussion(null, id);
        } else {
            const popupSelector = '#discussion-' + disc.id;
            bootstrap.Modal.getOrCreateInstance(popupSelector).show()
        }
    }
}

function traiterMessage(event) {
    console.log('Received event', event);
    const data = JSON.parse(event.data);
    console.log('Received data', data);
    disc = _.find(discussions, {id: data.message.dialog.id});
    if (!disc) {
        console.error('Aucune discussion trouvée', data.message.dialog.id);
        return;
    }
    ajouterMessage(disc, data.message);
    const id = parseInt(disc.owner.id == user ? disc.opponent.id : disc.owner.id);
    const selector = `#discussion-${id} .scroll`;
    const $el = $(selector);
    if ($el.length) scrollToEnd($el.get(0));
    else console.log('No element ?');
    console.log('Sender', data.message.sender.pk, user);
    if (data.message.sender.pk != user) msgAlert.play();
}

function chargerMessages(disc) {
    $('.messages').html("");
    $.post(`/discussions/${disc.id}/messages`, {})
        .done(function (result) {
            const messages = result.messages;
            //console.log("Liste des messages", messages);
            messages.forEach(msg => {
                ajouterMessage(disc, msg)
            });
            popupId = disc.owner.id == user ? disc.opponent.id : disc.owner.id;
            const popupSelector = '#discussion-' + popupId;
            const $scroll = $(popupSelector + ' .scroll');
            scrollToEnd($scroll.get(0));
        })
        .fail(function () {
            console.error("Impossible de récupérer la liste des messages");
        });
}

function marquerMessagesLus(disc) {
    $.post(`/discussions/${disc.id}/messages_lus`, {
        receiver: user
    })
        .done(function (result) {
            console.log("Messages marqués comme lus");
            disc.num_messages = 0;
            afficherDiscussions(discussions);
        })
        .fail(function () {
            console.error("Impossible de marquer les messages comme lus");
        });
}

function ajouterMessage(disc, msg) {
    let html;
    let heure;
    if (moment(msg.modified).isSame(moment(), 'day')) {
        heure = moment(msg.modified).format('HH:mm')
    } else {
        heure = moment(msg.modified).format('ddd D MMM, HH:mm')
    }
    //console.log('Message sender', msg);
    if (msg.sender.pk == user) {
        html = tempMsgOut({heure: heure, msg: msg.text});
    } else {
        html = tempMsgIn({heure: heure, msg: msg.text, sender: msg.sender.titre_nom});
    }
    popupId = disc.owner.id == user ? disc.opponent.id : disc.owner.id;
    console.log(`#discussion-${popupId}`);
    $(`#discussion-${popupId} .messages`).append(html);
}

function afficherDiscussions(discussions) {
    console.log("Liste des discussions", discussions);
    console.log("Liste des utilisateurs", users);
    const msgNonLus = _.sumBy(discussions, i => i.num_messages);
    console.info('Msg non lus', msgNonLus);
    $('#msg_non_lus').text(msgNonLus).css('visibility', msgNonLus>0 ? 'visible' : 'hidden');
    users = _.map(users, u => {
        const disc = _.find(discussions, d => {
            //console.log('Comparing', d.owner.id, u.pk);
            //console.log('Comparing', d.opponent.id, u.pk);
            return d.owner.id == u.pk || d.opponent.id == u.pk
        });
        u.num_messages = disc ? disc.num_messages : 0;
        return u;
    });
    const html = tempDiscussionItem({users: users});
    $('#liste_utilisateurs').html(html);
}

function ouvrirDiscussion(event, pk) {
    event && event.preventDefault();
    if (pk == user) {
        console.error('Impossible de démarrer une discussion avec soi-même');
        return;
    }
    console.log('Ouverture discussion', pk);
    KTDrawer.hideAll();
    const popupSelector = '#discussion-' + pk;
    if (!$(popupSelector).length) {
        // La popup n'existe pas, donc il faut la créer
        let opponent = _.find(users, {pk: pk});
        let popup = tempDiscussionPopup({id: pk, nom: opponent.titre_nom, enligne: opponent.enligne});
        $('#discussions-container').append(popup);
        const $scroll = $(popupSelector + ' .scroll');
        /*const ps = new PerfectScrollbar($scroll.get(0), {
            wheelSpeed: 0.5,
            swipeEasing: true,
            //wheelPropagation: (options.windowScroll === false ? false : true),
            minScrollbarLength: 40,
            maxScrollbarLength: $scroll.attr('data-height'),
            suppressScrollX: true
        });*/
        popups.push(bootstrap.Modal.getOrCreateInstance(popupSelector).show());
        scrollToEnd($scroll.get(0));
    } else {
        bootstrap.Modal.getOrCreateInstance(popupSelector).show();
    }

    let disc = trouverDiscussion(pk);
    if (!disc) {
        console.log('Aucune discussion trouvée');
        // Créer une nouvelle discussion
        $.post(`/discussions/ajouter`, {
            owner: user,
            opponent: pk
        })
            .done(function (result) {
                discussions.push(result.discussion);
                chargerMessages(result.discussion);
                connecter(result.discussion.id);
                marquerMessagesLus(result.discussion);
                console.log("Discussion créée");
            })
            .fail(function () {
                console.error("Impossible de créer une discussion");
            });
    } else {
        console.log('Discussion trouvée, connexion', disc);
        chargerMessages(disc);
        connecter(disc.id);
        marquerMessagesLus(disc);
    }
    return false;
}

function envoyerMessage(discussion, message) {
    console.info('Envoi message', message);
    let socket = sockets[discussion.id];
    if (!socket) {
        log.error('Socket non valide');
        return;
    }
    let msg = JSON.stringify({
        message: message,
        sender: user
    });
    socket.send(msg);
}

function scrollToEnd(container) {
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 500);
}

function modifierStatutConnexion(user) {

}

$(document).ready(() => {

    tempDiscussionItem = _.template(unescapeTemplate($('#template-user-discussion').html()));
    tempDiscussionPopup = _.template(unescapeTemplate($('#template-discussion-popup').html()));
    tempMsgIn = _.template(unescapeTemplate($('#template-message-in').html()));
    tempMsgOut = _.template(unescapeTemplate($('#template-message-out').html()));

    // Charger la liste des utilisateurs
    $.post(`/liste_utilisateurs`, {})
        .done(function (result) {
            users = _.filter(result.users, u => u.pk != user);
            //console.log("Liste des utilisateurs", users);

            // Charger la liste des discussions
            $.post(`/liste_discussions/${user}`, {})
                .done(function (result) {
                    discussions = result.discussions;
                    afficherDiscussions(discussions);
                })
                .fail(function () {
                    console.error("Impossible de récupérer la liste des discussions de l'utilisateur", user);
                });
        })
        .fail(function () {
            console.error("Impossible de récupérer la liste des utilisateurs");
        });

    initaliserEventSocket();

    $('#discussions-container').on('keyup', '.message-text', function (e) {
        if (e.keyCode === 13) {  // enter, return
            const id = $(this).attr('data-id');
            console.info('Envoi message dans la discussion', id);
            let msg = $(this).val();
            if (!msg) return; // Message vide
            $(this).val('');
            let disc = trouverDiscussion(id);
            if (!disc) {
                log.error("La discussion {} n'existe pas", id);
            } else {
                envoyerMessage(disc, msg);
            }
        }
    });

    window.onbeforeunload = function() {
        _.each(sockets, s => s.close());
        eventSocket && eventSocket.close();
    }

    //setupChatWebSocket();
    //scrollToLastMessage();


});