window.addEventListener('DOMContentLoaded', () => {
    const themes = [
        "ambiance",
        "chaos",
        "chrome",
        "cloud9_day",
        "cloud9_night",
        "cloud9_night_low_color",
        "clouds",
        "clouds_midnight",
        "cobalt",
        "crimson_editor",
        "dawn",
        "dracula",
        "dreamweaver",
        "eclipse",
        "github",
        "gob",
        "gruvbox",
        "gruvbox_dark_hard",
        "gruvbox_light_hard",
        "idle_fingers",
        "iplastic",
        "katzenmilch",
        "kr_theme",
        "kuroir",
        "merbivore",
        "merbivore_soft",
        "mono_industrial",
        "monokai",
        "nord_dark",
        "one_dark",
        "pastel_on_dark",
        "solarized_dark",
        "solarized_light",
        "sqlserver",
        "terminal",
        "textmate",
        "tomorrow",
        "tomorrow_night",
        "tomorrow_night_blue",
        "tomorrow_night_bright",
        "tomorrow_night_eighties",
        "twilight",
        "vibrant_ink",
        "xcode",
    ];

    const websocket = new WebSocket(`ws://${window.location.host}/update-code`);
    const Range = ace.require('ace/range').Range

    ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1");
    const editor = ace.edit('editor', {
        mode: "ace/mode/python",
        selectionStyle: "text"
    });
    editor.setOptions({
        autoScrollEditorIntoView: true,
        copyWithEmptySelection: true,
    });
    const problems = {};
    let currentProblemID;
    const editorElement = document.querySelector("#editor");
    const gutterElement = document.querySelector(".ace_gutter");
    let selectionObject = editor.getSession().getSelection();
    for(const scrollbar of document.querySelectorAll('.ace_scrollbar')) {
        scrollbar.addEventListener('scroll', (e) => {
            for(const cursorData of Object.values(otherCursors)){
                if(!cursorData.cursor) return
                let cursor = cursorData.cursor

                const {pageX, pageY} = editor.renderer.textToScreenCoordinates(cursorData.pos.row, cursorData.pos.column)
                if (pageX <= editorElement.offsetLeft  +gutterElement.offsetWidth
                    || pageX >= editorElement.offsetLeft + editorElement.offsetWidth +gutterElement.offsetWidth
                    || pageY <= editorElement.offsetTop
                    || pageY >= editorElement.offsetTop + editorElement.offsetHeight) {
                    cursor.style.display = 'none';
                } else {
                    cursor.style.display = 'block';
                }
                cursor.style.left = (
                    pageX
                    + 'px');
                cursor.style.top = (
                    pageY
                    +'px'
                );
            }
        })
    }
    let theme_ = localStorage.getItem('theme') || 'textmate'
    editor.setTheme(`ace/theme/${theme_}`);
    const themeSelect = document.querySelector('select#theme-select');
    const editorFontSize = document.querySelector('input#editor-font-size');
    for(let theme of themes) {
        const node = document.createElement('option');
        if (theme == theme_){
            node.selected = true;
        }
        node.value = `https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-${theme}.min.js`;
        node.text = theme;
        themeSelect.appendChild(node);
    }

    themeSelect.addEventListener('change', (e) => {
        const themeCDN = themeSelect.value;
        let theme = themeCDN.slice('https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-'.length, -('.min.js'.length));
        if(!themes.includes(theme)) return;

        editor.setTheme(`ace/theme/${theme}`);
        localStorage.setItem('theme', theme);
    });

    let editorFontSizeValue = localStorage.getItem('editorFontSize') || '12';
    editor.setFontSize(editorFontSizeValue + 'px');
    editorFontSize.value = editorFontSizeValue;
    let editorLineHeight = editor.getFontSize().slice(0,-2) * (7 / 6);

    editorFontSize.addEventListener('change', (e) => {
        if(editorFontSize.value > 50) {
            editorFontSize.value = 50;
        } else if(editorFontSize.value < 10) {
            editorFontSize.value = 10;
        }
        editor.setFontSize(editorFontSize.value + 'px');
        editorLineHeight = editor.getFontSize().slice(0,-2) * (7 / 6);
        for(const key in otherCursors) {
            const cursor = otherCursors[key].cursor
            cursor.style.height = editorLineHeight + 'px';
            cursor.style.width = 1 + Math.floor(editor.getFontSize().slice(0,-2) / 25) + 'px';
            cursor.style.fontSize = editor.getFontSize();
            cursor.style.setProperty('--font-size', editor.getFontSize());

            const {row, column} = otherCursors[key].pos
            const {pageX, pageY} = editor.renderer.textToScreenCoordinates(row, column);
            cursor.style.left = (
                pageX
                + 'px');
            cursor.style.top = (
                pageY
                +'px'
            );
        }
        localStorage.setItem('editorFontSize', editorFontSize.value)
    });




    const otherCursors = {};
    function addOtherCursor(pos, name, problemID) {
        let cursor;
        const {pageX, pageY} = editor.renderer.textToScreenCoordinates(pos.row, pos.column)
        if(!otherCursors.hasOwnProperty(name)){
            cursor = document.createElement('div');
            cursor.style.width = 1 + Math.floor(editor.getFontSize().slice(0,-2) / 25) + 'px';
            cursor.style.height = editorLineHeight + 'px';
            cursor.setAttribute('user-name', name);
            cursor.style.backgroundColor = 'red';
            cursor.style.position = 'absolute';
            cursor.classList.add('cursor');
            cursor.style.fontSize = editor.getFontSize();
            cursor.style.setProperty('--font-size', editor.getFontSize());



            otherCursors[name] = {
                cursor: cursor,
                pos: {
                    row: pos.row,
                    column: pos.column,
                },
                problemID: problemID
            };
            document.body.appendChild(cursor);
        } else {
            cursor = otherCursors[name].cursor;
            otherCursors[name].pos = {
                row: pos.row,
                column: pos.column,
            }
            otherCursors[name].problemID = problemID;
        }


        cursor.style.left = (
            pageX
            + 'px');
        cursor.style.top = (
            pageY
            +'px'
        );

        if(problemID != currentProblemID) {
            cursor.style.display = 'none';
        } else if (problemID == currentProblemID) {
            cursor.style.display = 'block';
        }

    }
    let userId, token;
    editor.addEventListener('change', (e) => {
        if (!(editor.curOp && editor.curOp.command.name)) return
        websocket.send(JSON.stringify({
            data: {
                text: e.lines,
                start: e.start,
                end: e.end,
            },
            action: e.action,
            user_id: userId,
            token: token,
            problem_id: currentProblemID
        }));
    });

    editor.addEventListener('focus', (e) => {
        websocket.send(JSON.stringify({
            data: {
                pos: selectionObject.getCursor(),
            },
            action: 'cursorMove',
            user_id: userId,
            token: token,
            problem_id: currentProblemID
        }));
    });


    selectionObject.addEventListener('changeCursor', (e) => {
        if (!(editor.curOp && editor.curOp.command.name)) return
        websocket.send(JSON.stringify({
            data: {
                pos: selectionObject.getCursor(),
            },
            action: 'cursorMove',
            user_id: userId,
            token: token,
            problem_id: currentProblemID
        }));

        for(const cursorData of Object.values(otherCursors)){
            const {pageX, pageY} = editor.renderer.textToScreenCoordinates(cursorData.pos.row, cursorData.pos.column)
            let cursor = cursorData.cursor

            if (pageX <= editorElement.offsetLeft  +gutterElement.offsetWidth
                || pageX >= editorElement.offsetLeft + editorElement.offsetWidth +gutterElement.offsetWidth
                || pageY <= editorElement.offsetTop
                || pageY >= editorElement.offsetTop + editorElement.offsetHeight) {
                cursor.style.display = 'none';
            }else {
                cursor.style.display = 'block';
            }
            cursor.style.left = (
                pageX
                + 'px');
            cursor.style.top = (
                pageY
                +'px'
            );
            }
    });
    const gameTab =document.getElementById('game');
    const chatTab =document.getElementById('chat');
    const votingTab =document.getElementById('voting');

    const tabs = document.querySelector('#editor-tabs');
    const info = document.querySelector('#info');
    const chatNav = document.createElement('button');
    const messages = document.getElementById('messages');
    chatNav.id = "chat-nav";
    chatNav.innerText = 'Chat'
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    const gameNav = document.querySelector('#code-nav');
    gameNav.style.backgroundColor = 'grey'

    const votingNav = document.createElement('button');

    votingNav.id = "voting-nav";
    votingNav.innerText = 'Voting';
    const usersList = document.getElementById('users');
    let role;
    let currentButton;
    websocket.addEventListener('message', ({data}) => {
        data = JSON.parse(data);
        if(data.action == 'assign_id') {
            userId = data.user_id;
            token = data.token;
            for(let [index, problem] of data.data.problems.entries()) {
                problem = JSON.parse(problem)
                let session;
                if (index == 0){
                    session = editor.getSession();
                } else {
                    session = ace.createEditSession("", "ace/mode/python")
                }
                problems[problem.id] = {
                    problem: problem.prompt,
                    problemID: problem.id,
                    difficulty: problem.difficulty,
                    session: session
                }

                session.addEventListener('changeScrollTop', () => {
                    for(const cursorData of Object.values(otherCursors)){
                        const {pageX, pageY} = editor.renderer.textToScreenCoordinates(cursorData.pos.row, cursorData.pos.column)
                        let cursor = cursorData.cursor
                        if (pageX <= editorElement.offsetLeft  +gutterElement.offsetWidth
                            || pageX >= editorElement.offsetLeft + editorElement.offsetWidth +gutterElement.offsetWidth
                            || pageY <= editorElement.offsetTop
                            || pageY >= editorElement.offsetTop + editorElement.offsetHeight) {
                            cursor.style.display = 'none';
                        }else {
                            cursor.style.display = 'block';
                        }
                        cursor.style.left = (
                            pageX
                            + 'px');
                        cursor.style.top = (
                            pageY
                            +'px'
                        );
                        }
                });
                const button = document.createElement('button');
                if (index == 0){
                    currentButton = button;
                    currentButton.style.backgroundColor = 'grey'
                }
                button.innerText = `Problem ${problem.id}`;
                button.setAttribute('problem-id', problem.id)
                button.addEventListener('click', (e) => {
                    currentButton.style.backgroundColor = 'white';
                    currentButton = e.target;
                    currentButton.style.backgroundColor = 'grey'

                    const problemID = e.target.getAttribute('problem-id');
                    for(const problem of Object.values(problems)){
                        if(problem.problemID == problemID){
                            editor.setSession(problem.session);
                            info.innerHTML = `
                                ${problem.problem}

                                Difficulty: ${problem.difficulty}
                            `;
                            currentProblemID = problem.problemID;
                        }
                    }

                    for(const key in otherCursors) {
                        if (otherCursors[key].problemID != currentProblemID) {
                            otherCursors[key].cursor.style.display = 'none';
                        } else if (otherCursors[key].problemID == currentProblemID) {
                            otherCursors[key].cursor.style.display = 'block';
                        }
                    }
                    selectionObject = editor.getSession().getSelection();

                    websocket.send(JSON.stringify({
                        data: {
                            pos: selectionObject.getCursor(),
                        },
                        action: 'cursorMove',
                        user_id: userId,
                        token: token,
                        problem_id: currentProblemID
                    }));
                })
                tabs.appendChild(button);
                if(index == 0 ){
                    info.innerHTML = `
                        ${problems[problem.id].problem}

                        Difficulty: ${problems[problem.id].difficulty}
                    `;
                    currentProblemID = problems[problem.id].problemID;
                }
            }

            websocket.send(JSON.stringify({
                data: {

                },
                action: 'request_code',
                user_id: userId,
                token: token,
                problem_id: -1
            }));
        } else if (['insert', 'remove', 'cursorMove'].includes(data.action)) {
            if(data.user_id == userId) return;
            let editorDocument;
            if(data.problem_id == currentProblemID){
                editorDocument = editor.getSession().getDocument();
            } else {
                editorDocument = problems[data.problem_id].session.getDocument();
            }

            if(data.action == 'insert'){
                editorDocument.insertMergedLines(data.data.start, data.data.text);

                addOtherCursor(data.data.end, data.user_id, data.problem_id);
            } else if (data.action == 'remove') {

                editorDocument.remove(new Range(
                    data.data.start.row,
                    data.data.start.column,
                    data.data.end.row,
                    data.data.end.column
                    )
                );


                addOtherCursor(data.data.start, data.user_id, data.problem_id);

            } else if (data.action == 'cursorMove'){

                addOtherCursor(data.data.pos, data.user_id, data.problem_id);
            }
        } else if (data.action =='game_end') {
            editor.setReadOnly(true);
            let code = {};
            for (const problem of Object.values(problems)) {
                code[problem.problemID] = problem.session.getDocument().getAllLines();
            }

            websocket.send(JSON.stringify({
                data: {
                    code: code,
                },
                action: 'submitCode',
                user_id: userId,
                token: token,
                problem_id : -1
            }));
            for(const cursorData of Object.values(otherCursors)){
                cursorData.cursor.style.display = 'none';
            }
            chatNav.addEventListener('click',(e) => {
                chatNav.style.backgroundColor = 'grey'
                gameNav.style.backgroundColor = 'white'
                votingNav.style.backgroundColor = 'white'

                gameTab.style.display=  'none';
                chatTab.style.display=  'flex';
                votingTab.style.display = 'none';

            })
            document.querySelector('header').appendChild(chatNav)
            document.querySelector('header').appendChild(votingNav)

            gameNav.addEventListener('click', (e) => {
                gameNav.style.backgroundColor = 'grey'
                chatNav.style.backgroundColor = 'white'
                votingNav.style.backgroundColor = 'white'

                gameTab.style.display=  'grid';

                chatTab.style.display=  'none';
                votingTab.style.display = 'none';
                editor.resize(true)

            })

            for(const user of data.data.users){
                const userElement = document.createElement("div");
                userElement.className = 'user'
                const userName = document.createElement("span");
                userName.innerText = user;
                const voteButton = document.createElement("button");
                userElement.appendChild(userName)
                userElement.appendChild(voteButton)
                voteButton.addEventListener('click', (e) => {
                    websocket.send(JSON.stringify({
                        data: {
                            voted: user,
                        },
                        action: 'vote',
                        user_id: userId,
                        token: token,
                        problem_id : -1
                    }));
                })
                voteButton.innerText = 'Vote'
                usersList.appendChild(userElement)
            }

            votingNav.addEventListener('click', (e) => {
                chatNav.style.backgroundColor = 'white'
                gameNav.style.backgroundColor = 'white'
                votingNav.style.backgroundColor = 'grey'

                gameTab.style.display=  'none';
                chatTab.style.display=  'none';
                votingTab.style.display = 'flex';
            })

            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                if(!chatInput.value) return
                websocket.send(JSON.stringify({
                    data: {
                        message: chatInput.value,
                    },
                    action: 'chat_message',
                    user_id: userId,
                    token: token,
                    problem_id : -1
                }));
                chatInput.value = '';
            })

        }else if (data.action == 'request_code') {
            let code = {};
            for (const problem of Object.values(problems)) {
                code[problem.problemID] = problem.session.getDocument().getAllLines();
            }
            websocket.send(JSON.stringify({
                data: {
                    code: code,
                },
                action: 'send_requested_code',
                user_id: userId,
                token: token,
                problem_id : -1
            }));
        } else if(data.action == 'send_requested_code') {
            for (const [problemID, code] of Object.entries(data.data.code)) {

                let document = problems[problemID].session.getDocument()
                document.replace(new Range(0,0,document.getLength(), document.getAllLines().slice(-1).length), code.join('\n'))
            }

        } else if (data.action == 'chat_message'){
            const message = document.createElement('p');
            message.innerText = `${data.user_id}: ${data.data.message}`;
            messages.appendChild(message)
            message.scrollIntoView()
        } else if (data.action == 'role') {
            role = data.data.role;
            alert('You are the '+ role)
        } else if (data.action == 'result') {
            alert(`You ${data.data.result}! The Bugposter was ${data.data.bugposter}`)
        } else {
            console.log('Unknown action: '+ data.action);
        }
    });
    window.addEventListener('resize', (e) => {
        for(const cursorData of Object.values(otherCursors)){
            const {pageX, pageY} = editor.renderer.textToScreenCoordinates(cursorData.pos.row, cursorData.pos.column)
            let cursor = cursorData.cursor
            if (pageX <= editorElement.offsetLeft  +gutterElement.offsetWidth
                || pageX >= editorElement.offsetLeft + editorElement.offsetWidth +gutterElement.offsetWidth
                || pageY <= editorElement.offsetTop
                || pageY >= editorElement.offsetTop + editorElement.offsetHeight) {
                cursor.style.display = 'none';
            }else {
                cursor.style.display = 'block';
            }
            cursor.style.left = (
                pageX
                + 'px');
            cursor.style.top = (
                pageY
                +'px'
            );
            }
    });
});
