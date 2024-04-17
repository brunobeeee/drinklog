import * as bootstrap from 'bootstrap'
import 'youtube-background';

const videoBackgrounds = new VideoBackgrounds('[data-vbg]', {
    'inline-styles': true
});

const videoElement = document.querySelector('[data-vbg]');

if (videoElement) {
    // get the first instance instance by UID
    const videoInstance = videoBackgrounds.get(videoElement);
    // add the element to the factory instance
    videoBackgrounds.add(firstElement);
    // true if the video is playing, false if the video is not playing
    console.log(firstInstance.playing);

    // true if video is muted, false if video is not muted
    console.log(firstInstance.muted);

    // true if the video is intersecting the viewport, false if the video is not intersecting the viewport.
    console.log(firstInstance.isIntersecting); 
}