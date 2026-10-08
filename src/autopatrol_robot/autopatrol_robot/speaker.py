import shutil
import subprocess

import rclpy
from autopatrol_interfaces.srv import SpeachText
from rclpy.node import Node


class Speaker(Node):
    def __init__(self):
        super().__init__('speaker')
        self.speech_service = self.create_service(
            SpeachText, 'speech_text', self.speak_text_callback
        )

        # The book uses the Python espeakng package. It is optional here:
        # when it is not installed, this node keeps the service online and
        # logs the requested speech text so the patrol workflow can continue.
        self._speaker = None
        try:
            import espeakng

            self._speaker = espeakng.Speaker()
            self._speaker.voice = 'zh'
            self.get_logger().info('Using Python espeakng speaker backend.')
        except Exception as exc:
            self._espeak_command = shutil.which('espeak-ng') or shutil.which('espeak')
            if self._espeak_command:
                self.get_logger().warn(
                    f'Python espeakng unavailable ({exc}); using {self._espeak_command}.'
                )
            else:
                self.get_logger().warn(
                    f'espeakng unavailable ({exc}); speech will be logged only.'
                )

    def speak_text_callback(self, request, response):
        self.get_logger().info(f'Speech request: {request.text}')

        if self._speaker is not None:
            try:
                self._speaker.say(request.text)
                self._speaker.wait()
            except Exception as exc:
                self.get_logger().error(f'Python TTS failed: {exc}')
                response.result = False
                return response
        elif getattr(self, '_espeak_command', None):
            # Keep speech execution synchronous so the patrol node knows the
            # announcement has finished before it starts the next action.
            completed = subprocess.run(
                [self._espeak_command, request.text],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if completed.returncode != 0:
                self.get_logger().error(
                    f'Command-line TTS failed with exit code {completed.returncode}.'
                )
                response.result = False
                return response
        else:
            # Logging is useful for a headless CI/simulation session, but it
            # is not successful audio synthesis. Let the caller distinguish
            # that condition from a real announcement.
            response.result = False
            return response

        response.result = True
        return response


def main(args=None):
    rclpy.init(args=args)
    node = Speaker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
