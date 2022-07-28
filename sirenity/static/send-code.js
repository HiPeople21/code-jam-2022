const placeholderProblems = [
    {
        id: 1,
        prompt: 'hello there',
        difficulty: 10
    },
    {
        id: 2,
        prompt: 'General Kenobi',
        difficulty: 20
    },
    {
        id: 3,
        prompt: 'IDK what happens next',
        difficulty: 100
    }
]


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
    let selectionObject = editor.getSession().getSelection();


    const themeSelect = document.querySelector('select#theme-select');
    const editorFontSize = document.querySelector('input#editor-font-size');
    for(const theme of themes) {
        const node = document.createElement('option');
        if (theme == 'textmate'){
            node.selected = true;
        }
        node.value = `https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-${theme}.min.js`;
        node.text = theme;
        themeSelect.appendChild(node);
    }

    themeSelect.addEventListener('change', (e) => {
        const themeCDN = themeSelect.value;
        const theme = themeCDN.slice('https://cdnjs.cloudflare.com/ajax/libs/ace/1.8.1/theme-'.length, -('.min.js'.length));
        if(!themes.includes(theme)) return;

        editor.setTheme(`ace/theme/${theme}`);
    });



    let editorLineHeight = editor.getFontSize() * (7 / 6);
    editor.setFontSize('12px');

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
    });

    const tabs = document.querySelector('#editor-tabs');
    const info = document.querySelector('#info');
    websocket.addEventListener('message', ({data}) => {
        data = JSON.parse(data);
        if(data.action == 'assign_id') {
            userId = data.user_id;
            token = data.token;
            for(let [index, problem] of data.problems.entries()) {
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
                const button = document.createElement('button');
                button.innerText = `Problem ${problem.id}`;
                button.setAttribute('problem-id', problem.id)
                button.addEventListener('click', (e) => {

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
            }
            info.innerHTML = `
                ${Object.values(problems)[0].problem}

                Difficulty: ${Object.values(problems)[0].difficulty}
            `;
            currentProblemID = Object.values(problems)[0].problemID;

        } else {
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
            } else {
                console.log('Unknown action: '+ data.action);
            }
        }
    });



});
