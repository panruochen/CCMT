# YUNZ

This is a collection of misc tools

##### vimrc
<table>
  <tbody align="left">
    <tr>
      <th>Mode</th>
      <th>Keymap</th>
      <th>Filtype</th>
      <th>Functions</th>
    </tr>
    <tr>
      <td>N</td>
      <td>%es</td>
      <td>all</td>
      <td>Expand leading tables to spaces within the whole file according to the value of &TS.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>%et</td>
      <td>all</td>
      <td>Expand leading spaces to tables within the whole file according to the value of &TS.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\es</td>
      <td>all</td>
      <td>Expand leading tables to spaces within selected lines according to the value of &TS.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\et</td>
      <td>all</td>
      <td>Expand leading spaces to tables within selected lines according to the value of &TS.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\a</td>
      <td>all</td>
      <td>Align all columns for the selected lines.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\s</td>
      <td>all</td>
      <td>Mapping to</br><u>:s/\&lt;pattern\&gt;//</u></br> taking the current word as the pattern.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\s</td>
      <td>all</td>
      <td>Mapping to</br><u>&lt;,&gt;,:s/\&lt;pattern\&gt;//</u></br> taking the current word as the pattern.</td>
    </tr>
    <tr>
      <td>V</td>
      <td><b>&lt;TAB&gt;</b></td>
      <td>all</td>
      <td>Add one tab at the front of every selected line.</td>
    </tr>
    <tr>
      <td>V</td>
      <td><b>&lt;BS&gt;</b></td>
      <td>all</td>
      <td>Remove one tab from the front of every selected line.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\u</td>
      <td>all</td>
      <td>Turn the word under the cursor to lower-case.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\U</td>
      <td>all</td>
      <td>Turn the word under the cursor to upper-case.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\]</td>
      <td>all</td>
      <td>Toggle line number display.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\[</td>
      <td>all</td>
      <td>Toggle relative line number display.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\n</td>
      <td>C/C++/H</td>
      <td>Select the entire function including the cursor.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\b</td>
      <td>C/C++/H</td>
      <td>Backward select the {} block including the cursor.</td>
    </tr>
    <tr>
      <td>N</td>
      <td>\f</td>
      <td>C/C++/H</td>
      <td>Forward select the {} block including the cursor.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\1</td>
      <td>C/C++/H</td>
      <td>Copy the first columns within the selected lines.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\2</td>
      <td>C/C++/H</td>
      <td>Copy the second columns within the selected lines.</td>
    </tr>
    <tr>
      <td>V</td>
      <td>\x</td>
      <td>C/C++/H</td>
      <td>Paste a printf(...) statement according to columns copied by \1 or \2 beforehand.</td>
    </tr>
    <tr>
      <td>N</td>
      <td><b>&lt;F9&gt;</b></td>
      <td>Make</td>
      <td>Select the $(...) block including the cursor.</td>
    </tr>
  </tbody>
</table>



