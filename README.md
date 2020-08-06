<style>
/* Container for flexboxes */
.row {
  display: flex;
  flex-wrap: wrap;
}

/* Create four equal columns */
.column {
  flex: 25%;
  padding: 20px;
}

/* On screens that are 992px wide or less, go from four columns to two columns */
/*@media screen and (max-width: 992px) {
  .column {
    flex: 50%;
  }
}
*/

/* On screens that are 600px wide or less, make the columns stack on top of each other instead of next to each other */
@media screen and (max-width: 992px) {
  .row {
    flex-direction: column;
  }
}
</style>

Read [my blog](https://soderlind.no/) or [follow @soderlind on Twitter](https://twitter.com/soderlind).

<div class="row">
  <div class="column">
    <h2>On my blog</h2>
    <p>
	<!-- blog starts -->
	<!-- blog ends -->
	</p>
  </div>

  <div class="column">
    <h2>Read</h2>
        <p>
	<!-- read starts -->
	<!-- read ends -->
	</p>
  </div>

  <div class="column">
    <h2>Tweets</h2>
        <p>
	<!-- tweet starts -->
	<!-- tweet ends -->
	</p>
  </div>
</div>

<a href="https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/">How this works</a>
