import pygame
import random
import math
import sys
import os

def get_correct_path(relative_path):
  base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
  return os.path.join(base_path, relative_path)

class Life:

  def __init__(self, surface: pygame.Surface, rect: pygame.Rect = None):
    self.surface = surface
    self.rect    = rect    


class Item:

  def __init__(self, surface: pygame.Surface, label: str, rect: pygame.Rect = None):
    self.surface = surface
    self.rect    = rect
    self.label   = label


# Class to manage the falling of the items
class FallingItems:

  bad_items_surface:  list[Item] = []
  good_items_surface: list[Item] = []
  items_list: list[Item] = []


  def __init__(self, player_width):

    # Bad items
    FallingItems.bad_items_surface.append(Item(pygame.image.load(get_correct_path("rotten_lemon.png")).convert_alpha(), "bad"))
    FallingItems.bad_items_surface.append(Item(pygame.image.load(get_correct_path("rotten_apple.png")).convert_alpha(), "bad"))

    # Good items
    FallingItems.good_items_surface.append(Item(pygame.image.load(get_correct_path("banana.png")).convert_alpha(), "good"))
    FallingItems.good_items_surface.append(Item(pygame.image.load(get_correct_path("apple.png")).convert_alpha(), "good"))
    FallingItems.good_items_surface.append(Item(pygame.image.load(get_correct_path("orange_1.png")).convert_alpha(), "good"))
    FallingItems.good_items_surface.append(Item(pygame.image.load(get_correct_path("orange_2.png")).convert_alpha(), "good"))
    FallingItems.good_items_surface.append(Item(pygame.image.load(get_correct_path("mango.png")).convert_alpha(), "good"))

    self.set_items(player_width)


  def set_items(self, player_width) -> None:
    
    # Resize the items
    for item in (FallingItems.bad_items_surface + FallingItems.good_items_surface):
      proportion = item.surface.get_height() / item.surface.get_width() # Get the image proportion item at 0 index is the surface

      new_width  = 0.6 * player_width
      new_height = new_width * proportion
      
      item_new_size: tuple[int, int] = (new_width, new_height)
      item.surface = pygame.transform.smoothscale(item.surface, item_new_size)
  

  def spawn_random_item(self, difficulty: int) -> None:

    # Choosing a random item to spawn
    random_item: Item = random.choice((difficulty * FallingItems.bad_items_surface) + FallingItems.good_items_surface)
      
    # Choosing a random spot to spawn
    rightmost_spawn_pos = 0
    leftmost_spawn_pos  = Game.screen_width - random_item.surface.get_width() # Item at 0 index is the surface

    item_spawn_y: float = 0 - random_item.surface.get_height()

    item_spawn_x: float = random.randint(int(rightmost_spawn_pos), int(leftmost_spawn_pos))
    item_object: pygame.Rect = pygame.Rect(item_spawn_x, item_spawn_y, random_item.surface.get_width(), random_item.surface.get_height())

    FallingItems.items_list.append(Item(random_item.surface, random_item.label, item_object))


  def fall(self, object_speed: float, object: Item) -> None:

    object.rect.y += int(object_speed)


# Player mechanics
class Player:
  
  def set_player(self, screen_height: int, screen_width: int) -> None:

    # Loading the player image
    self.player = pygame.image.load(get_correct_path("basket.png")).convert_alpha()

    # Scaling the player
    player_og_width = self.player.get_width()
    player_og_height = self.player.get_height()
    player_scaling_factor = 0.06
    player_new_size = (player_og_width * player_scaling_factor, player_og_height * player_scaling_factor)
    self.player = pygame.transform.smoothscale(self.player, player_new_size)

    # Initial coordinates of the player
    self.player_x: float = (screen_width / 2) - (self.player.get_width() / 2)            # Player starts in the middle of the screen
    self.player_y: float = screen_height - self.player.get_height() - (0.005 * screen_height) # Fixed player pos on y axis
    self.player_pos: tuple[float, float] = self.player_x, self.player_y

    # Player hitbox
    self.player_object = pygame.Rect(self.player_x, self.player_y, self.player.get_width() - (0.1 * self.player.get_width()), self.player.get_height() - (0.1 * self.player.get_height()))
  

  def move_left(self, player_speed: float) -> None:
    self.player_x -= player_speed
    self.player_object.topleft = (int(self.player_x), int(self.player_y))
    self.player_pos = self.player_x, self.player_y


  def move_right(self, player_speed: float) -> None:
    self.player_x += player_speed
    self.player_object.topleft = (int(self.player_x), int(self.player_y))
    self.player_pos = self.player_x, self.player_y


# Game, objects integrations and score
class Game:

  # Game settings
  screen_width:  int = 640
  screen_height: int = 640
  screen_size:   tuple[int, int] = (screen_width, screen_height)
  
  # Other variables 
  running: bool   = False
  lost:    bool   = False
  first_item_fell = False
  objects_on_screen: list[tuple[pygame.Surface, tuple[float, float]]] = []
  player_speed_multiplier: float = 350.0
  item_fall_speed_multiplier: float = 15000.0
  items_spawn_rate_milis: int = 700
  score: int = 0
  played_time: int = 0
  lifes: list[Life] = []


  def __init__(self) -> None:
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    self.set_settings()
    self.start_game()


  def set_settings(self) -> None:
    self.screen = pygame.display.set_mode(Game.screen_size)
    pygame.display.set_caption("Catch Game by Arthur Marchi")
    pygame.display.set_icon(pygame.image.load(get_correct_path("basket.png")))
    self.clock  = pygame.time.Clock()
    self.player: Player = Player()
    self.ITEM_SHOULD_FALL = pygame.USEREVENT
    self.GAME_LOST = pygame.USEREVENT + 1
    self.font = pygame.font.SysFont("ComicSans", 30)
    pygame.mixer.music.load(get_correct_path("catching_se.mp3"))


  def set_background(self) -> None:

    # Loading the background image
    self.background = pygame.image.load(get_correct_path("background.png")).convert_alpha()

    # Scaling the background
    bg_og_width = self.background.get_width()
    bg_og_height = self.background.get_height()
    bg_scaling_factor = 0.7
    bg_new_size = (int(bg_og_width * bg_scaling_factor), int(bg_og_height * bg_scaling_factor))
    self.background = pygame.transform.smoothscale(self.background, bg_new_size)
    
    # Initial coordinates of the background
    self.backgrond_x:  float = 0
    self.background_y: float = 0
    self.background_pos: tuple[float, float] = self.backgrond_x, self.background_y


  def update_clock(self) -> None:
    self.delta_time = self.clock.tick(60) / 1000


  def paint_screen(self) -> None:

    self.screen.blit(self.background, self.background_pos) # Always update the background

    if Game.lost:
      self.gamelost_surface = self.font.render(f"YOU LOST, SCORE: {Game.score}", True, (0, 0, 0))
      self.gamelost_rect = self.gamelost_surface.get_rect()
      self.gamelost_rect.center = (Game.screen_width // 2, Game.screen_height // 2)
      self.screen.blit(self.gamelost_surface, self.gamelost_rect)

    else:
      self.screen.blit(self.score_surface, self.score_rect) # Also update the score
      self.screen.blit(self.timer_surface, self.timer_rect)
      for life in Game.lifes:
        self.screen.blit(life.surface, (life.rect.x, life.rect.y))
      
      for object in Game.objects_on_screen:
        self.screen.blit(object[0], object[1]) # object 0 = surface; object 1 = pos

    pygame.display.update()
    Game.objects_on_screen.clear()


  def start_game(self) -> None:
    Game.running = True

    # Set the score text
    self.score_surface = self.font.render(str(Game.score), True, (0, 0, 0))
    self.score_rect = self.score_surface.get_rect()
    self.score_rect.center = (Game.screen_width - 0.95 * Game.screen_width, Game.screen_height - 0.95 * Game.screen_height)

    # Set the timer text
    self.timer_surface = self.font.render(str(Game.played_time), True, (0, 0, 0))
    self.timer_rect = self.timer_surface.get_rect()
    self.timer_rect.center = (Game.screen_width // 2 - (Game.screen_width * 0.05), Game.screen_height - 0.95 * Game.screen_height)

    # Set the game lifes
    for i in range(3):
      life_surface = pygame.image.load(get_correct_path("life.png")).convert_alpha()
      life_surface = pygame.transform.smoothscale(life_surface, (0.08 * life_surface.get_width(), 0.08 * life_surface.get_height()))
      life_rect    = life_surface.get_rect()

      life_rect.x = Game.screen_width - 0.08 * Game.screen_width - ((0.08 * Game.screen_width) * i)
      life_rect.y = Game.screen_height - 0.97 * Game.screen_height

      Game.lifes.append(Life(life_surface, life_rect))
 
    # Set player and background
    self.player.set_player(Game.screen_height, Game.screen_width)
    self.set_background()
    # Append the player to the objects on screen list
    Game.objects_on_screen.append((self.player.player, self.player.player_pos))
    
    # Paint starting screen
    self.paint_screen()

    # Falling items
    self.items = FallingItems(self.player.player.get_width())

    # Timer to trigger falling item event
    pygame.time.set_timer(self.ITEM_SHOULD_FALL, Game.items_spawn_rate_milis)

    self.game_loop()

  
  def game_loop(self) -> None:
    while Game.running:
      if not Game.lost:
        self.update_clock()

        # Update the played time
        Game.played_time = round(pygame.time.get_ticks() / 1000, 2)
        self.timer_surface = self.font.render(str(Game.played_time), True, (0, 0, 0))

        # Update player speed and item falling speed according to the time passed in the game
        punishment =  math.pow(self.played_time, 2) / max(1, self.score)
        self.player_speed: float    = max(Game.player_speed_multiplier * self.delta_time, min((1300 * self.delta_time), (Game.player_speed_multiplier * self.delta_time) + (0.1 * Game.played_time)))
        self.item_fall_speed: float = max(Game.item_fall_speed_multiplier * self.delta_time, (Game.item_fall_speed_multiplier * self.delta_time) + math.pow((0.3 * Game.played_time), 2) + punishment)

        # Handling movement (key presses)
        keys = pygame.key.get_pressed()

        # To the left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

          if self.player.player_x > 0:
            self.player.move_left(self.player_speed)
    
        # To the right
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

          if self.player.player_x < Game.screen_width - self.player.player.get_width():
            self.player.move_right(self.player_speed)
        
        
        # Update world
        if Game.first_item_fell:
          for item in FallingItems.items_list[:]:
            self.items.fall(self.item_fall_speed * self.delta_time, item)

            if self.player.player_object.colliderect(item.rect):
              FallingItems.items_list.remove(item)
              
              # If the item is labeled as good -> increase score
              if item.label == "good":
                Game.score += 100
                self.score_surface = self.font.render(str(Game.score), True, (0, 0, 0))
                pygame.mixer.music.play()

              # If the item is labeled as bad -> loses life
              if item.label == "bad" and len(Game.lifes) > 0:
                Game.lifes.pop()
                pygame.mixer.music.play()

          # Only put the items in the list if they are in the world (screen)
          FallingItems.items_list = [item for item in FallingItems.items_list if item.rect.y < Game.screen_height]

          # If all lifes are lost -> loses the game
          if len(Game.lifes) <= 0:
            self.game_lost_event = pygame.event.Event(self.GAME_LOST)
            pygame.event.post(self.game_lost_event)
        

        # Sets the objects to be painted and then paint them
        Game.objects_on_screen.append((self.player.player, self.player.player_pos))
        if Game.first_item_fell:
          for item in FallingItems.items_list:
            Game.objects_on_screen.append((item.surface, (item.rect.x, item.rect.y)))

        self.paint_screen() 


      # Handling events
      for event in pygame.event.get():

        # Game lost
        if event.type == self.GAME_LOST:
          Game.lost = True
          self.paint_screen()

        # Item should drop
        if event.type == self.ITEM_SHOULD_FALL:
          self.items.spawn_random_item(2)
          Game.first_item_fell = True

          # Increase items falling rate according to the time passed in the game
          Game.items_spawn_rate_milis = max(250 , Game.items_spawn_rate_milis - (0.1 * Game.played_time))
          pygame.time.set_timer(self.ITEM_SHOULD_FALL, int(Game.items_spawn_rate_milis))

        # Closing
        if event.type == pygame.QUIT:
          Game.running = False 
    

    pygame.quit()


def main() -> None:
  game = Game()


if __name__ == "__main__":
  main()
