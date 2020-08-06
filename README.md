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
* [How to import native ES modules in WordPress](https://soderlind.no/how-to-import-native-es-modules-in-wordpress/) - 04.12.2019
* [add_theme_support( 'disable_block_style')](https://soderlind.no/add-theme-support-disable-block-style/) - 07.11.2019
* [Hide block styles in Gutenberg](https://soderlind.no/hide-block-styles-in-gutenberg/) - 18.10.2019
* [Local by Flywheel: Using WordMove to mirror sites](https://soderlind.no/local-by-flywheel-using-wordmove-to-mirror-sites/) - 30.09.2019
* [Learn to code!](https://soderlind.no/learn-to-code/) - 21.12.2018
<!-- blog ends -->
	</p>
  </div>

  <div class="column">
    <h2>Read</h2>
        <p>
	<!-- read starts -->
* [Miscellaneous Developer Focused Changes in WordPress 5.5](https://make.wordpress.org/core/2020/07/29/miscellaneous-developer-focused-changes-in-wordpress-5-5) - 29.07.2020
* [New in PHP 8](https://stitcher.io/blog/new-in-php-8) - 25.07.2020
* [New wp_get_environment_type() function in WordPress 5.5](https://make.wordpress.org/core/2020/07/24/new-wp_get_environment_type-function-in-wordpress-5-5) - 24.07.2020
* [RSS Feeds for WordPress Plugin and Theme Support Forum Topics and Replies](https://kaspars.net/blog/wp-org-support-forum-rss-replies) - 24.07.2020
* [New XML Sitemaps Functionality in WordPress 5.5](https://make.wordpress.org/core/2020/07/22/new-xml-sitemaps-functionality-in-wordpress-5-5) - 23.07.2020
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
