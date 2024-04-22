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
    videoBackgrounds.add(videoElement);
}