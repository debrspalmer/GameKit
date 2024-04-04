async function loadFriends(usteamid) {
    const apiUrl = `/api/friends?steamid=${usteamid}`;

    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
            document.getElementById("friends_list").innerHTML = `<p>Private</p>`;
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Iterate over each friend in the response
        document.getElementById("friends_list").innerHTML = `<ul>`;
        let i = 0;
        for (const steamid in data) {
            i++;
            if (i === 10) { break; }
            if (data.hasOwnProperty(steamid)) {
                const friend = data[steamid];
                // Log or display the formatted output (avatar - personaname)
                console.log(`${friend.avatar} - ${friend.personaname}`);
                document.getElementById("friends_list").innerHTML += `<li><a href='/user/${steamid}'>${friend.personaname}</a></li>`;
            }
        }
        document.getElementById("friends_list").innerHTML += `</ul>`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
async function loadGames(usteamid) {
    const apiUrl = `/api/games?steamid=${usteamid}`;
    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
        document.getElementById("friends_list").innerHTML = `<p>Private</p>`;
        throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        data.games.sort((a, b) => a.name.localeCompare(b.name));
        let gamelist = "";
        for (let i = 0; i < data.games.length; i++) {
            const game = data.games[i];
            console.log(game);
            //console.log(`http://media.steampowered.com/steamcommunity/public/images/apps/${game.appid}/${game.img_icon_url}.jpg - ${game.name} - ${game.playtime_forever}`);
            gamelist += `<a onclick="selectgame('${game.appid}','${game.name}')">${game.name}</a>`;
        }
        document.getElementById("gamedropdown-list").innerHTML = gamelist;
        // Iterate over each friend in the response
        document.getElementById("games_list").innerHTML = `<ul>`;
        let i = 0;
        for (const gamedata in data['games']) {
            i++;
            if (i == 8) { break; }
            const game = data['games'][gamedata];
            console.log(`http://media.steampowered.com/steamcommunity/public/images/apps/${game.appid}/${game.img_icon_url}.jpg - ${game.name}`);
            document.getElementById("games_list").innerHTML += `<li>${game.name}</li>`;
        }
        document.getElementById("games_list").innerHTML += `</ul>`;

        const sortedGames = data['games'].sort((a, b) => b.playtime_forever - a.playtime_forever);
        // Display the top 10 most played games
        document.getElementById("most_played_games").innerHTML = `<ol>`;
        for (let i = 0; i < Math.min(3, sortedGames.length); i++) {
            const game = sortedGames[i];
            console.log(`http://media.steampowered.com/steamcommunity/public/images/apps/${game.appid}/${game.img_icon_url}.jpg - ${game.name} - ${game.playtime_forever}`);
            document.getElementById("most_played_games").innerHTML += `<li>${Math.floor(game.playtime_forever/60)} hours - ${game.name}</li>`;
        }
        document.getElementById("most_played_games").innerHTML += `</ol>`;

        const topsortedGames = data['games']
        .sort((a, b) => b.playtime_forever - a.playtime_forever)
        .slice(0, 50)
        .map(game => game.appid)
        .join(',');

        console.log(topsortedGames);
        const apiUrl = `/api/achievments?steamid=${usteamid}&appids=${topsortedGames}`;
        
        fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
            document.getElementById("friends_list").innerHTML = `<p>Private</p>`;
            throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            
            // Filter only achievements that have been achieved
            const filteredData = data.Response.map(item => {
                if (item.playerstats && item.playerstats.achievements) {
                const achievements = item.playerstats.achievements.filter(achievement => achievement.achieved === 1);
                return { playerstats: { achievements: achievements }, ...item.playerstats }
                } else {
                return item;
                }
            });
            console.log(filteredData);
            
            // Sorting the achievements by unlocktime in descending order
            responseData = filteredData.flat().filter(data => data.playerstats?.achievements?.length > 0);
            responseData.sort((a, b) => b.playerstats.achievements[0].unlocktime - a.playerstats.achievements[0].unlocktime);

            // Creating the ordered list HTML
            let ol = document.createElement('ol');

            // Iterating through the achievements and adding them to the list
            for (let i = 0; i < Math.min(responseData.length, 5); i++) {
                let achievement = responseData[i].playerstats.achievements[0];
                let gameName = responseData[i].gameName; // Accessing gameName property here
                let apiname = achievement.apiname;
                let unlocktime = new Date(achievement.unlocktime * 1000).toLocaleDateString(); // Converting Unix timestamp to readable date
            
                let li = document.createElement('li');
                li.textContent = `${gameName} - ${apiname} - ${unlocktime}`;
                ol.appendChild(li);
            }

            // Setting the inner HTML of the div with ID "newest_achievement"

            document.getElementById('newest_achievement').innerHTML = '';
            document.getElementById('newest_achievement').appendChild(ol);
            
            })
            .catch(error => {
                console.error('Error:', error);
            });
            
        })
    .catch(error => {
        console.error('Error:', error);
    });
}

/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  function filterFunction() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdown");
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
      txtValue = a[i].textContent || a[i].innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
      } else {
        a[i].style.display = "none";
      }
    }
  }
function selectgame(appid,appname) {
    document.getElementById("GameSelection").innerHTML = appname;
    console.log(appid);
    console.log(appname);
    appidselection = appid;
}
let appidselection = 0;