# Video-Info-Plugin-Mod--1
The Movie DB Online Movie Database (search.py Alternative)

I have been using Video Station by Synology for several years now. One of the pet peaves I have always had is that the metadata retrieval system lacked in the ability to deal with how I named my files. I have chosen to name them in the conventional sort order method. I also include such information as the resolution, the year released, the rating, and the IMDb number. This has caused me lots of problems and numerous manual searching. With my TV episodes I have cosen to incude the episode date and the episode name. This has never seemed to be a problem with season one and two, but following season fail for some reason.

Well, Synology has finally made it so we can create our own Video Info Plugins. They have created and excellent <a href="https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf?_ga=2.110080901.1614377027.1626195829-311373403.1626195829">Developer's Guide</a> to assist us in that endevour. Unfortunately, I have been unable to "Add" my own plugin using VideoStaton v3.0.1-2067 on DSM 7. The message being given on the user interface is "The plugin does not work. Please check your Internet connection." I have been discussing this in the Synology Forum located here: <a href="How can I install My Own Video Info Plugin?">How can I install My Own Video Info Plugin?</a>

This mod I am presenting IS NOT FOR EVERYONE!

The one I present here is the plugin changes I made to my plugin. I have modified the existing "search.py" in the existing plugin offered by Synology. This is located at the following location: "/var/packages/VideoStation/target/plugins/syno_themoviedb/"

This plugin changes the "sort" title to a "proper" title and removes the excess data. My qualifier for the search is a double space. ("  ") I use this following the sort title in all my files.
 <table style="width:100%">
  <tr>
    <th>Example</th>
    <th>Output</th>
  </tr>
  <tr>
    <td>Fighting 69th, The  (1080p)  [1940] {Passed} - tt0032467</td>
    <td>The Fighting 69th</td>
  </tr>
  <tr>
    <td>Country Wedding, A  (Hallmark)  (1080p)  [2015] (TV) {TV-G} - tt4814436</td>
    <td>A Country Wedding</td>
  </tr>
  <tr>
    <td>Godwink Christmas, A - Meant for Love  (HM&M)  (1080p)  [2019] (TV) {NR} - tt10926350</td>
    <td>A Godwink Christmas: Meant for Love</td>
  </tr>
  <tr>
    <td>Every Day's a Holiday  (1080p)  [1937] {Approved} - tt0028843</td>
    <td>Every Day's a Holiday</td>
  </tr>
  <tr>
    <td>Bewitched - S03 E01 - (1966-09-15) - Nobody's Perfect</td>
    <td>Bewitched - S03 E01</td>
  </tr>
</table> 
